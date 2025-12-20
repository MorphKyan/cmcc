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

  return window.location.origin;
};

// Get WebSocket URL based on current protocol and backend configuration
const getWebSocketUrl = (clientId) => {
  const backendUrl = getBackendUrl();

  // Parse the backend URL and construct WebSocket URL
  try {
    const url = new URL(backendUrl);
    // Always use wss:// protocol for WebSocket connection
    return `wss://${url.host}/audio/ws/${clientId}`;
  } catch (error) {
    console.warn('Invalid backend URL, using window.location:', backendUrl, error);
    // Fallback: use current page's host for WebSocket with wss:// protocol
    return `wss://${window.location.host}/audio/ws/${clientId}`;
  }
};

export const config = {
  getBackendUrl,
  getWebSocketUrl
};