// Frontend configuration
// This file provides configuration for backend connection

// Get backend URL from environment variable or use default
// In production, this should be set via environment variables
// In development, it can be configured in .env files or hardcoded

const getBackendUrl = () => {
  // Check if we have a VITE_BACKEND_URL environment variable
  let url = import.meta.env.VITE_BACKEND_URL || window.location.origin;

  // Remove trailing slash if present
  if (url.endsWith('/')) {
    url = url.slice(0, -1);
  }

  return url;
};

// Get WebSocket URL based on current protocol and backend configuration
const getWebSocketUrl = (clientId) => {
  const backendUrl = getBackendUrl();

  // Parse the backend URL and construct WebSocket URL
  try {
    const url = new URL(backendUrl);
    const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${url.host}/api/audio/ws/${clientId}`;
  } catch (error) {
    console.warn('Invalid backend URL, using window.location:', backendUrl, error);
    // Fallback: use current page's protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/api/audio/ws/${clientId}`;
  }
};

export const config = {
  getBackendUrl,
  getWebSocketUrl
};