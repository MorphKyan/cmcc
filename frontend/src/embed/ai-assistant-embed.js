/**
 * AI Assistant Embeddable Widget
 * 
 * This module provides an embeddable AI Assistant widget that can be
 * integrated into any H5 page with minimal configuration.
 * 
 * Usage:
 *   <script src="ai-assistant.umd.js"></script>
 *   <script>
 *     AIAssistant.init({
 *       backendUrl: 'https://your-backend.com',
 *       position: { bottom: '20px', right: '20px' },
 *       theme: 'dark'
 *     });
 *   </script>
 */

import { createApp, h } from 'vue';
import AIAssistantWidget from '../components/AIAssistantWidget.vue';

// Global state
let appInstance = null;
let containerElement = null;

/**
 * Configuration options for the AI Assistant widget
 * @typedef {Object} AIAssistantConfig
 * @property {string} [backendUrl] - Backend WebSocket URL (default: auto-detect)
 * @property {Object} [position] - Initial position { top, bottom, left, right }
 * @property {string} [theme] - Theme: 'light' or 'dark' (default: 'dark')
 * @property {string} [containerId] - Custom container ID (default: 'ai-assistant-container')
 */

/**
 * Default configuration
 */
const defaultConfig = {
    backendUrl: '',
    position: { bottom: '20px', right: '20px' },
    theme: 'dark',
    containerId: 'ai-assistant-container'
};

/**
 * Initialize the AI Assistant widget
 * @param {AIAssistantConfig} config - Configuration options
 */
function init(config = {}) {
    // Merge with defaults
    const mergedConfig = { ...defaultConfig, ...config };

    // Prevent double initialization
    if (appInstance) {
        console.warn('[AIAssistant] Already initialized. Call destroy() first to reinitialize.');
        return;
    }

    // Create container element
    containerElement = document.createElement('div');
    containerElement.id = mergedConfig.containerId;
    containerElement.style.cssText = 'position: fixed; z-index: 99999; pointer-events: none;';
    document.body.appendChild(containerElement);

    // Create Shadow DOM for style isolation (optional, for better encapsulation)
    let mountTarget = containerElement;
    if (typeof containerElement.attachShadow === 'function') {
        try {
            const shadow = containerElement.attachShadow({ mode: 'open' });
            // Create a wrapper inside shadow DOM
            const wrapper = document.createElement('div');
            wrapper.style.cssText = 'pointer-events: auto;';
            shadow.appendChild(wrapper);
            mountTarget = wrapper;

            // Inject styles into shadow DOM
            const styleSheet = document.createElement('style');
            styleSheet.textContent = getWidgetStyles();
            shadow.appendChild(styleSheet);
        } catch (e) {
            console.warn('[AIAssistant] Shadow DOM not available, using regular DOM');
        }
    }

    // Create Vue app
    appInstance = createApp({
        render() {
            return h(AIAssistantWidget, {
                backendUrl: mergedConfig.backendUrl,
                theme: mergedConfig.theme,
                initialPosition: mergedConfig.position
            });
        }
    });

    // Mount the app
    appInstance.mount(mountTarget);

    console.log('[AIAssistant] Initialized successfully');
}

/**
 * Destroy the AI Assistant widget
 */
function destroy() {
    if (appInstance) {
        appInstance.unmount();
        appInstance = null;
    }

    if (containerElement && containerElement.parentNode) {
        containerElement.parentNode.removeChild(containerElement);
        containerElement = null;
    }

    console.log('[AIAssistant] Destroyed');
}

/**
 * Get widget styles as string (for Shadow DOM injection)
 */
function getWidgetStyles() {
    return `
    .ai-assistant-widget {
      position: fixed;
      z-index: 99999;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    }
    .ai-btn {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      transition: all 0.3s ease;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .ai-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    .ai-btn:active { transform: scale(0.98); }
    .ai-btn:disabled { opacity: 0.7; cursor: not-allowed; }
    .ai-icon { width: 28px; height: 28px; color: white; }
    .ai-icon svg { width: 100%; height: 100%; }
    .is-recording .ai-btn {
      background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
      box-shadow: 0 4px 15px rgba(245, 87, 108, 0.5);
    }
    .is-connecting .ai-btn {
      background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    }
    .pulse-ring {
      position: absolute;
      width: 100%;
      height: 100%;
      border-radius: 50%;
      border: 2px solid rgba(245, 87, 108, 0.6);
      animation: pulse 1.5s ease-out infinite;
    }
    @keyframes pulse {
      0% { transform: scale(1); opacity: 1; }
      100% { transform: scale(1.8); opacity: 0; }
    }
    .spin { animation: spin 1s linear infinite; }
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .status-indicator {
      position: absolute;
      top: -30px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      white-space: nowrap;
    }
    .result-panel {
      position: absolute;
      bottom: 70px;
      right: 0;
      width: 300px;
      max-height: 400px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
      overflow: hidden;
    }
    .theme-dark .result-panel {
      background: #1e1e2e;
      color: #cdd6f4;
    }
    .result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      font-weight: 600;
    }
    .theme-dark .result-header {
      border-bottom-color: rgba(255, 255, 255, 0.1);
    }
    .close-btn {
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: inherit;
      opacity: 0.6;
      transition: opacity 0.2s;
    }
    .close-btn:hover { opacity: 1; }
    .result-content {
      padding: 16px;
      max-height: 300px;
      overflow-y: auto;
    }
    .result-text {
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.5;
    }
    .result-placeholder {
      color: #888;
      text-align: center;
      padding: 20px;
    }
    .reconnect-overlay {
      position: absolute;
      bottom: 70px;
      right: 0;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px 16px;
      border-radius: 8px;
      font-size: 12px;
    }
    .reconnect-content {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .reconnect-spinner {
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
  `;
}

// Export API
export const AIAssistant = {
    init,
    destroy,
    version: '1.0.0'
};

// Auto-attach to window for UMD usage
if (typeof window !== 'undefined') {
    window.AIAssistant = AIAssistant;
}

export default AIAssistant;
