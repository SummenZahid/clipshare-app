// Get API URL from runtime config or environment variable or default
const getApiUrl = () => {
  // Check for runtime config (set by Docker entrypoint)
  if (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) {
    return window.APP_CONFIG.API_BASE_URL;
  }
  // Check for build-time environment variable
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  // Default fallback
  return 'http://localhost:8000/api';
};

export const API_BASE_URL = getApiUrl();

