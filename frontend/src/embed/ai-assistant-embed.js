/**
 * AI Assistant Embeddable Widget (Vanilla JS Version)
 * 
 * Features:
 * - Zero Vue dependency (Pure JS)
 * - Built-in AudioWorkletProcessor (No external file needed)
 * - Auto-connect & Auto-reconnect (5s interval)
 * - Draggable Floating UI
 * - WebSocket communication for ASR & LLM
 */

// Inlined AudioWorklet to avoid 404s on external files
const AUDIO_PROCESSOR_CODE = `
class AudioProcessor extends AudioWorkletProcessor {
  process(inputs, outputs) {
    const input = inputs[0];
    if (input.length > 0 && input[0].length > 0) {
      const channelData = input[0];
      // Convert Float32 to Int16 PCM (16kHz expected by backend)
      const int16Array = new Int16Array(channelData.length);
      for (let i = 0; i < channelData.length; i++) {
        int16Array[i] = Math.max(-32768, Math.min(32767, Math.round(channelData[i] * 32767)));
      }
      this.port.postMessage(int16Array.buffer, [int16Array.buffer]);
    }
    return true;
  }
}
registerProcessor('audio-processor', AudioProcessor);
`;

class AIAssistantWidget {
  constructor(config) {
    this.config = {
      backendUrl: config.backendUrl || '',
      position: config.position || { bottom: '20px', right: '20px' },
      theme: config.theme || 'dark',
      containerId: config.containerId || 'ai-assistant-container'
    };

    // State
    this.isRecording = false;
    this.isConnected = false;
    this.isReconnecting = false;
    this.socket = null;
    this.audioContext = null;
    this.mediaStream = null;
    this.workletNode = null;
    this.reconnectTimer = null;
    this.clientId = `client-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

    // Drag State
    this.isDragging = false;
    this.dragStartTime = 0;
    this.dragStartX = 0;
    this.dragStartY = 0;
    this.elmStartX = 0;
    this.elmStartY = 0;

    // Init
    this.initUI();
    this.initStyles();
    this.connect(); // Auto-connect on start
  }

  // ============================================
  // UI Construction
  // ============================================
  initUI() {
    // Container
    this.container = document.createElement('div');
    this.container.id = this.config.containerId;
    this.container.className = `ai-assistant-widget theme-${this.config.theme}`;
    Object.assign(this.container.style, {
      position: 'fixed',
      zIndex: '99999',
      ...this.config.position
    });

    // Button
    this.btn = document.createElement('button');
    this.btn.className = 'ai-btn';
    this.btn.title = '长按说话 / Double Click to Drag';
    this.btn.innerHTML = `
            <div class="ai-icon">
                <svg id="icon-mic" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                <svg id="icon-stop" style="display:none" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-4h2v2h-2zm1.61-9.96c-2.06-.3-3.88.97-4.43 2.79-.18.58.26 1.17.87 1.17h.2c.41 0 .74-.29.88-.67.32-.89 1.27-1.5 2.3-1.28.95.2 1.65 1.13 1.57 2.1-.1 1.34-1.62 1.63-2.45 2.88 0 .01-.01.01-.01.02-.01.02-.02.03-.03.05-.09.15-.18.32-.25.5-.01.03-.03.05-.04.08-.01.02-.01.04-.02.07-.12.34-.2.75-.2 1.25h2c0-.42.11-.77.28-1.07.02-.03.03-.06.05-.09.08-.14.18-.27.28-.39.01-.01.02-.03.03-.04.1-.12.21-.23.33-.34.96-.91 2.26-1.65 1.99-3.56-.24-1.74-1.61-3.21-3.35-3.47z"/></svg>
                <svg id="icon-spin" class="spin" style="display:none" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
            </div>
            <div class="pulse-ring"></div>
        `;

    // Status
    this.statusEl = document.createElement('div');
    this.statusEl.className = 'status-indicator';
    this.statusEl.textContent = '初始化...';
    this.statusEl.style.display = 'none';

    // Result Panel
    this.resultPanel = document.createElement('div');
    this.resultPanel.className = 'result-panel';
    this.resultPanel.style.display = 'none';
    this.resultPanel.innerHTML = `
            <div class="result-header">
                <span>AI 响应</span>
                <button class="close-btn">×</button>
            </div>
            <div class="result-content">
                <div class="result-text"></div>
            </div>
        `;

    // Assemble
    this.container.appendChild(this.btn);
    this.container.appendChild(this.statusEl);
    this.container.appendChild(this.resultPanel);
    document.body.appendChild(this.container);

    // Events
    this.bindEvents();
  }

  initStyles() {
    const css = `
            .ai-assistant-widget { font-family: system-ui, sans-serif; }
            .ai-btn {
                width: 56px; height: 56px; border-radius: 50%; border: none;
                cursor: pointer; display: flex; align-items: center; justify-content: center;
                position: relative; transition: all 0.3s ease;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                color: white; z-index: 10;
            }
            .ai-btn:hover { transform: scale(1.05); }
            .ai-btn:active { transform: scale(0.98); }
            .ai-assistant-widget.recording .ai-btn {
                background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
                box-shadow: 0 4px 15px rgba(245, 87, 108, 0.5);
            }
            .ai-assistant-widget.connecting .ai-btn {
                background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
                cursor: wait;
            }
            .ai-icon svg { width: 28px; height: 28px; }
            .pulse-ring {
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                border-radius: 50%; border: 2px solid rgba(245, 87, 108, 0.6);
                opacity: 0; pointer-events: none;
            }
            .ai-assistant-widget.recording .pulse-ring {
                animation: ai-pulse 1.5s ease-out infinite;
            }
            @keyframes ai-pulse {
                0% { transform: scale(1); opacity: 1; }
                100% { transform: scale(1.8); opacity: 0; }
            }
            .spin { animation: ai-spin 1s linear infinite; }
            @keyframes ai-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
            
            .status-indicator {
                position: absolute; top: -35px; left: 50%; transform: translateX(-50%);
                background: rgba(0,0,0,0.8); color: white; padding: 4px 12px;
                border-radius: 12px; font-size: 12px; white-space: nowrap; pointer-events: none;
            }
            
            .result-panel {
                position: absolute; bottom: 70px; right: 0; width: 300px; max-height: 400px;
                background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                display: flex; flex-direction: column; overflow: hidden;
            }
            .theme-dark .result-panel { background: #1e1e2e; color: #cdd6f4; }
            .result-header {
                display: flex; justify-content: space-between; align-items: center;
                padding: 12px 16px; border-bottom: 1px solid rgba(0,0,0,0.1); font-weight: 600;
            }
            .theme-dark .result-header { border-bottom: 1px solid rgba(255,255,255,0.1); }
            .close-btn { background: none; border: none; color: inherit; font-size: 20px; cursor: pointer; }
            .result-content { padding: 16px; overflow-y: auto; max-height: 340px; }
            .result-text { font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
        `;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
  }

  bindEvents() {
    const startEvents = ['mousedown', 'touchstart'];
    const moveEvents = ['mousemove', 'touchmove'];
    const endEvents = ['mouseup', 'touchend'];

    startEvents.forEach(evt => {
      this.btn.addEventListener(evt, this.onInteractStart.bind(this), { passive: false });
    });

    moveEvents.forEach(evt => {
      document.addEventListener(evt, this.onInteractMove.bind(this), { passive: false });
    });

    endEvents.forEach(evt => {
      document.addEventListener(evt, this.onInteractEnd.bind(this));
    });

    // Close panel
    this.resultPanel.querySelector('.close-btn').addEventListener('click', () => {
      this.resultPanel.style.display = 'none';
    });

    // Window resize handling
    window.addEventListener('resize', this.onWindowResize.bind(this));
  }

  onWindowResize() {
    if (!this.container) return;

    const rect = this.container.getBoundingClientRect();
    const w = window.innerWidth;
    const h = window.innerHeight;

    // Clamp values to keep distinct padding from edges (e.g. 10px)
    let newLeft = rect.left;
    let newTop = rect.top;

    // Check right edge
    if (newLeft + rect.width > w) {
      newLeft = w - rect.width - 10;
    }
    // Check bottom edge
    if (newTop + rect.height > h) {
      newTop = h - rect.height - 10;
    }
    // Check left edge
    if (newLeft < 0) newLeft = 10;
    // Check top edge
    if (newTop < 0) newTop = 10;

    // Apply if changed
    this.container.style.left = px(newLeft);
    this.container.style.top = px(newTop);

    // Also reset right/bottom if they were set (force using top/left after first move)
    this.container.style.right = 'auto';
    this.container.style.bottom = 'auto';
  }

  // ============================================
  // Interaction Logic (Drag & Long Press)
  // ============================================
  onInteractStart(e) {
    if (this.isConnecting && !this.isConnected) return;

    // Prevent default only for touch to stop scrolling/zooming while interacting
    if (e.type === 'touchstart') e.preventDefault();

    const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
    const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;
    const now = Date.now();

    // Check Double Click (Double Tap)
    if (now - this.lastClickTime < 300) {
      // Double Click -> Drag Mode
      this.isDragging = true;
      this.prepareDrag(clientX, clientY);

      // Cancel any pending long press or click actions
      this.clearTimers();
    } else {
      // First Click / Potential Long Press
      this.lastClickTime = now;
      this.isDragging = false;
      this.startX = clientX;
      this.startY = clientY;

      // Schedule Long Press Record
      this.longPressTimer = setTimeout(() => {
        if (!this.isDragging) {
          this.isRecordingPTT = true;
          this.startRecording();
        }
      }, 500); // 500ms threshold for long press
    }
  }

  onInteractMove(e) {
    if (!this.isDragging && !this.longPressTimer && !this.isRecordingPTT) return;

    const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
    const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;

    if (this.isDragging) {
      e.preventDefault();
      this.doDrag(clientX, clientY);
    } else {
      // Check if moved too much to cancel long press
      const dx = Math.abs(clientX - this.startX);
      const dy = Math.abs(clientY - this.startY);
      if (dx > 10 || dy > 10) {
        this.clearTimers();
      }
    }
  }

  onInteractEnd(e) {
    // Cleanup Drag
    if (this.isDragging) {
      this.isDragging = false;
    }

    // Cleanup Long Press / PTT
    if (this.isRecordingPTT) {
      this.stopRecording();
      this.isRecordingPTT = false;
    }

    // Cleanup Pending Timer (Short click)
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer);
      this.longPressTimer = null;
      // Handle Short Click (Optional: Show hint)
      // console.log('Short click - ignored');
    }
  }

  prepareDrag(clientX, clientY) {
    this.dragStartX = clientX;
    this.dragStartY = clientY;
    const rect = this.container.getBoundingClientRect();
    this.elmStartX = rect.left;
    this.elmStartY = rect.top;

    // Switch to left/top positioning
    this.container.style.right = 'auto';
    this.container.style.bottom = 'auto';
    this.container.style.left = px(this.elmStartX);
    this.container.style.top = px(this.elmStartY);
  }

  doDrag(clientX, clientY) {
    const dx = clientX - this.dragStartX;
    const dy = clientY - this.dragStartY;

    let newX = this.elmStartX + dx;
    let newY = this.elmStartY + dy;

    // Bounds
    const w = window.innerWidth;
    const h = window.innerHeight;
    newX = Math.max(0, Math.min(newX, w - 60));
    newY = Math.max(0, Math.min(newY, h - 60));

    this.container.style.left = px(newX);
    this.container.style.top = px(newY);
  }

  clearTimers() {
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer);
      this.longPressTimer = null;
    }
  }

  // ============================================
  // WebSocket Logic
  // ============================================
  connect() {
    if (this.socket) return;

    this.updateStatus('连接中...', true);

    let url = this.config.backendUrl;
    // Basic URL normalization
    if (!url.startsWith('ws')) {
      const loc = window.location;
      const protocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
      // If empty, try to derive or use default (assuming proxy)
      if (!url) url = `${protocol}//${loc.host}/audio/ws`;
      else if (url.startsWith('/')) url = `${protocol}//${loc.host}${url}`;
      else url = `${protocol}//${url}`;
    }

    // Append client ID if not present
    if (!url.includes('/ws/')) {
      url = url.replace(/\/$/, '') + '/' + this.clientId;
    } else if (!url.endsWith(this.clientId)) {
      // Assume url already has structure, do nothing or append?
      // The backend expects /audio/ws/{client_id}
    }

    // Safety: Ensure it ends with client id if generic path provided
    if (url.endsWith('/ws')) {
      url += '/' + this.clientId;
    }

    console.log('[AIAssistant] Connecting to:', url);

    try {
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        console.log('[AIAssistant] Connected');
        this.isConnected = true;
        this.isReconnecting = false;
        this.updateStatus('');

        // Send metadata
        this.socket.send(JSON.stringify({
          type: 'config',
          sampleRate: 16000,
          channelCount: 1,
          sampleSize: 16
        }));
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (e) {
          console.error('Msg Parse Error', e);
        }
      };

      this.socket.onclose = (event) => {
        console.log('[AIAssistant] Closed', event.code);
        this.cleanup(false);
        this.scheduleReconnect();
      };

      this.socket.onerror = (e) => {
        console.error('[AIAssistant] Error', e);
        // OnError usually precedes OnClose
      };

    } catch (e) {
      console.error(e);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.isReconnecting) return;
    this.isReconnecting = true;
    this.isConnected = false;
    this.updateStatus('断开连接，5秒后重试...');

    console.log('[AIAssistant] Reconnecting in 5s...');
    this.reconnectTimer = setTimeout(() => {
      this.socket = null; // Ensure clean slate
      this.connect();
    }, 5000);
  }

  handleMessage(data) {
    this.resultPanel.style.display = 'flex';
    const txtEl = this.resultPanel.querySelector('.result-text');

    if (data.type === 'asr_result') {
      // ASR Update
      txtEl.textContent = `[听写] ${data.text}`;
    }
    else if (data.type === 'execution_summary') {
      // Overall execution summary
      txtEl.textContent += `\n[执行] ${data.summary}`;
    }
    else if (data.type === 'command_result') {
      // Individual command result (e.g. Local commands)
      // Only show if there is a message and it's successful
      if (data.result && data.result.success && data.result.message) {
        txtEl.textContent += `\n[操作] ${data.result.message}`;
      }
    }
    else if (data.type === 'command_error') {
      // Command Error
      if (data.error && data.error.message) {
        txtEl.textContent += `\n[错误] ${data.error.message}`;
      }
    }
    else if (data.type === 'system_message') {
      // System / LLM Feedback (e.g. "Cannot understand")
      txtEl.textContent += `\n[AI] ${data.message}`;
    }
    else if (data.text || data.result) {
      // Fallback / LLM Stream
      const content = data.text || data.result;
      txtEl.textContent = content;
    }

    // Auto scroll
    this.resultPanel.querySelector('.result-content').scrollTop = 99999;
  }

  // ============================================
  // Audio Logic
  // ============================================
  async startRecording() {
    if (!this.isConnected) {
      alert('未连接服务器');
      return;
    }

    // Quick resume if we are in trailing silence mode
    if (this.isTrailingSilence) {
      // console.log('[AIAssistant] Quick resume!');
      if (this.silenceTimer) clearTimeout(this.silenceTimer);
      this.isTrailingSilence = false;
      this.isRecording = true;
      this.updateStatus('正在录音...');
      this.updateIcons();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: false,
          noiseSuppression: true
        }
      });
      this.mediaStream = stream;

      this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });

      // Load Worklet from inline blob
      const blob = new Blob([AUDIO_PROCESSOR_CODE], { type: 'application/javascript' });
      const workletUrl = URL.createObjectURL(blob);
      await this.audioContext.audioWorklet.addModule(workletUrl);

      const source = this.audioContext.createMediaStreamSource(stream);
      this.workletNode = new AudioWorkletNode(this.audioContext, 'audio-processor');

      this.workletNode.port.onmessage = (e) => {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          if (this.isRecording) {
            this.socket.send(e.data);
          } else if (this.isTrailingSilence) {
            // Send silence buffer of same size to maintain timing
            const silence = new Int16Array(e.data.byteLength / 2);
            this.socket.send(silence.buffer);
          }
        }
      };

      source.connect(this.workletNode);
      this.workletNode.connect(this.audioContext.destination); // For "keeping alive" processing

      this.isRecording = true;
      this.isTrailingSilence = false; // Ensure flag is reset
      this.updateStatus('正在录音...');
      this.updateIcons();

      // Clear previous result
      this.resultPanel.querySelector('.result-text').textContent = "正在聆听...";

    } catch (e) {
      console.error('Recording failed:', e);
      alert('无法启动录音: ' + e.message);
      this.closeAudioResources();
    }
  }

  stopRecording() {
    this.isRecording = false;
    this.updateIcons();
    this.updateStatus(''); // Clear 'Recording...' status

    // Instead of closing immediately, enter trailing silence mode
    if (this.audioContext && this.workletNode) {
      this.isTrailingSilence = true;
      // console.log('[AIAssistant] Starting 1s silence...');

      if (this.silenceTimer) clearTimeout(this.silenceTimer);

      this.silenceTimer = setTimeout(() => {
        // console.log('[AIAssistant] Silence done, closing.');
        this.isTrailingSilence = false;
        this.closeAudioResources();
      }, 1000);
    } else {
      this.closeAudioResources();
    }
  }

  closeAudioResources() {
    this.isRecording = false;
    this.isTrailingSilence = false;
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
      this.silenceTimer = null;
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(t => t.stop());
      this.mediaStream = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    this.workletNode = null;
  }

  toggleRecording() {
    if (this.isRecording) {
      this.stopRecording();
    } else {
      this.startRecording();
    }
  }

  cleanup(full = true) {
    this.stopRecording();
    if (full) {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
      if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    }
  }

  // ============================================
  // Helpers
  // ============================================
  updateStatus(text, connecting = false) {
    this.statusEl.textContent = text;
    this.statusEl.style.display = text ? 'block' : 'none';
    this.container.classList.toggle('connecting', connecting);
  }

  updateIcons() {
    this.container.classList.toggle('recording', this.isRecording);
    const mic = this.btn.querySelector('#icon-mic');
    const stop = this.btn.querySelector('#icon-stop');
    mic.style.display = this.isRecording ? 'none' : 'block';
    stop.style.display = this.isRecording ? 'block' : 'none';
  }

  static init(config) {
    if (!window.__aiAssistantInstance) {
      window.__aiAssistantInstance = new AIAssistantWidget(config);
    }
  }

  static destroy() {
    if (window.__aiAssistantInstance) {
      window.__aiAssistantInstance.cleanup();
      document.body.removeChild(window.__aiAssistantInstance.container);
      window.__aiAssistantInstance = null;
    }
  }
}

// Helper
function px(v) { return v + 'px'; }

// Export
export const AIAssistant = AIAssistantWidget;

// Auto-expose to window if not standard module environment
if (typeof window !== 'undefined') {
  window.AIAssistant = AIAssistant;
}
