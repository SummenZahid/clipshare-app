#!/bin/sh
# Entrypoint script for React app to inject environment variables at runtime

# Set default API URL if not provided
API_URL="${REACT_APP_API_URL:-http://localhost:8000/api}"

# Generate config.js with the API URL
echo "Setting API URL to: $API_URL"
cat > /usr/share/nginx/html/config.js <<EOF
// Runtime configuration for ClipShare Frontend
// This file is generated at container startup
window.APP_CONFIG = {
  API_BASE_URL: '$API_URL'
};
EOF

# Start nginx
exec nginx -g "daemon off;"

