# ClipShare Docker Deployment

This folder contains Dockerfiles for deploying ClipShare to Azure.

## Files

- `Dockerfile.backend` - Flask/Python backend application
- `Dockerfile.frontend` - React frontend application with nginx
- `nginx.conf` - Nginx configuration for frontend
- `.dockerignore.backend` - Backend ignore patterns
- `.dockerignore.frontend` - Frontend ignore patterns

## Building Docker Images

### Backend

```bash
# From project root
docker build -f docker/Dockerfile.backend -t clipshare-backend:latest .
```

### Frontend

```bash
# From project root
docker build -f docker/Dockerfile.frontend -t clipshare-frontend:latest .
```

## Running Locally

### Backend

```bash
docker run -p 8000:80 \
  -e COSMOS_ENDPOINT=your_endpoint \
  -e COSMOS_KEY=your_key \
  -e STORAGE_CONNECTION_STRING=your_connection_string \
  clipshare-backend:latest
```

### Frontend

```bash
docker run -p 3000:80 \
  -e REACT_APP_API_URL=http://your-backend-url/api \
  clipshare-frontend:latest
```

## Azure Deployment

### Using Azure Container Registry (ACR)

1. **Create Azure Container Registry:**
   ```bash
   az acr create --resource-group <resource-group> --name <registry-name> --sku Basic
   ```

2. **Login to ACR:**
   ```bash
   az acr login --name <registry-name>
   ```

3. **Build and push backend:**
   ```bash
   az acr build --registry <registry-name> --image clipshare-backend:latest -f docker/Dockerfile.backend .
   ```

4. **Build and push frontend:**
   ```bash
   az acr build --registry <registry-name> --image clipshare-frontend:latest -f docker/Dockerfile.frontend .
   ```

### Using Azure App Service

1. **Create App Service Plans:**
   ```bash
   az appservice plan create --name <plan-name> --resource-group <resource-group> --sku B1 --is-linux
   ```

2. **Create Web App for Backend:**
   ```bash
   az webapp create --resource-group <resource-group> --plan <plan-name> --name <backend-app-name> --deployment-container-image-name <registry-name>.azurecr.io/clipshare-backend:latest
   ```

3. **Create Web App for Frontend:**
   ```bash
   az webapp create --resource-group <resource-group> --plan <plan-name> --name <frontend-app-name> --deployment-container-image-name <registry-name>.azurecr.io/clipshare-frontend:latest
   ```

4. **Configure Environment Variables for Backend:**
   ```bash
   az webapp config appsettings set --resource-group <resource-group> --name <backend-app-name> --settings \
     COSMOS_ENDPOINT=<your-endpoint> \
     COSMOS_KEY=<your-key> \
     STORAGE_CONNECTION_STRING=<your-connection-string>
   ```

5. **Configure Environment Variables for Frontend:**
   ```bash
   az webapp config appsettings set --resource-group <resource-group> --name <frontend-app-name> --settings \
     REACT_APP_API_URL=https://<backend-app-name>.azurewebsites.net/api
   ```

## Local Development with Docker Compose

From the project root:

```bash
# Build and start both services
docker-compose -f docker/docker-compose.yml up --build

# Run in detached mode
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Notes

- Backend runs on port 80 inside container (Azure requirement)
- Frontend runs on port 80 with nginx
- Backend uses gunicorn for production WSGI server
- Frontend build is optimized for production
- Both images are based on Alpine/slim images for smaller size
- Frontend uses runtime configuration via `config.js` for API URL
- Backend reads PORT from environment variable (defaults to 8000 locally, 80 in container)

