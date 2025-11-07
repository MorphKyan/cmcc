// Frontend configuration
// This file provides configuration for backend connection

// Get backend URL from environment variable or use default
// In production, this should be set via environment variables
// In development, it can be configured in .env files or hardcoded

const getBackendUrl = () => {
  // Check if we have a VITE_BACKEND_URL environment variable
  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL;
  }

  // Check if we're in production (built app)
  if (import.meta.env.PROD) {
    // In production, use the same origin as the frontend
    return window.location.origin;
  }

  // Default development backend URL
  return 'http://localhost:5000';
};

// Get WebSocket URL based on current protocol and backend configuration
const getWebSocketUrl = (clientId) => {
  const backendUrl = getBackendUrl();

  // Parse the backend URL
  try {
    const url = new URL(backendUrl);
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${url.host}/api/audio/ws/${clientId}`;
  } catch (error) {
    console.warn('Invalid backend URL, using default:', backendUrl, error);
    // Fallback to current implementation with protocol detection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Try to extract host from backendUrl if it's a simple string like "localhost:5000"
    let host = 'localhost:5000';
    if (backendUrl && backendUrl.startsWith('http')) {
      try {
        const tempUrl = new URL(backendUrl);
        host = tempUrl.host;
      } catch (e) {
        // Keep default host
      }
    } else if (backendUrl && backendUrl.includes(':')) {
      // Assume it's already a host:port format
      host = backendUrl;
    }
    return `${protocol}//${host}/api/audio/ws/${clientId}`;
  }
};

export const config = {
  getBackendUrl,
  getWebSocketUrl
};