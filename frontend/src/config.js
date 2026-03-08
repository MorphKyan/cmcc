// Frontend configuration
// This file provides configuration for backend connection

export const config = {
  getBackendUrl: () => {
    let url = import.meta.env.VITE_BACKEND_URL || window.location.origin;
    if (url.endsWith('/')) url = url.slice(0, -1);
    return url;
  },
  
  getBaseWebSocketUrl: () => {
    let backendUrl = import.meta.env.VITE_BACKEND_URL || window.location.origin;
    // 如果是相对路径 (如 /api)，自动补全为当前完整的域名
    if (backendUrl.startsWith('/')) {
      backendUrl = window.location.origin + backendUrl;
    }
    const url = new URL(backendUrl);
    const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    let basePath = url.pathname.endsWith('/') ? url.pathname.slice(0, -1) : url.pathname;
    
    return `${protocol}//${url.host}${basePath}/audio/ws`;
  },

  getWebSocketUrl: (clientId) => {
    return `${config.getBaseWebSocketUrl()}/${clientId}`;
  }
};