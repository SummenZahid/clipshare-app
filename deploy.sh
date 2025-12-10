#!/bin/bash
# ClipShare Quick Deployment Script
# This script automates the Azure deployment process

set -e  # Exit on error

# Configuration
RESOURCE_GROUP="clipshare-rg"
LOCATION="northeurope"
ACR_NAME="clipshareacr$(date +%s | tail -c 4)"
BACKEND_APP="clipshare-backend-$(whoami | tr -d '-' | tr '[:upper:]' '[:lower:]' | cut -c1-8)"
FRONTEND_APP="clipshare-frontend-$(whoami | tr -d '-' | tr '[:upper:]' '[:lower:]' | cut -c1-8)"
COSMOS_DB="clipshare-db-$(date +%s | tail -c 4)"
STORAGE_ACCOUNT="clipshare$(date +%s | tail -c 6)"

echo "🚀 ClipShare Deployment Script"
echo "================================"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if logged in
echo "📋 Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "⚠️  Not logged in to Azure. Please run: az login"
    exit 1
fi

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION 2>/dev/null || echo "Resource group already exists"

# Create Cosmos DB
echo "🗄️  Creating Cosmos DB..."
az cosmosdb create \
  --name $COSMOS_DB \
  --resource-group $RESOURCE_GROUP \
  --default-consistency-level Session \
  --locations regionName=$LOCATION failoverPriority=0 \
  2>/dev/null || echo "Cosmos DB already exists"

# Create database and container
echo "📊 Creating Cosmos DB database and container..."
az cosmosdb sql database create \
  --account-name $COSMOS_DB \
  --resource-group $RESOURCE_GROUP \
  --name clipsharedb \
  2>/dev/null || echo "Database already exists"

az cosmosdb sql container create \
  --account-name $COSMOS_DB \
  --resource-group $RESOURCE_GROUP \
  --database-name clipsharedb \
  --name videos \
  --partition-key-path "/id" \
  --throughput 400 \
  2>/dev/null || echo "Container already exists"

# Create storage account
echo "💾 Creating storage account..."
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2 \
  2>/dev/null || echo "Storage account already exists"

# Create storage container
echo "📁 Creating storage container..."
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query connectionString -o tsv)

az storage container create \
  --name videos \
  --connection-string "$STORAGE_CONNECTION_STRING" \
  --public-access blob \
  2>/dev/null || echo "Container already exists"

# Create Container Registry
echo "🐳 Creating Azure Container Registry..."
az acr create \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku Basic \
  --admin-enabled true \
  2>/dev/null || echo "ACR already exists"

# Create App Service Plan
echo "📱 Creating App Service Plan..."
az appservice plan create \
  --name clipshare-plan \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux \
  2>/dev/null || echo "App Service Plan already exists"

# Create Web Apps
echo "🌐 Creating Web Apps..."
az webapp create \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --plan clipshare-plan \
  --deployment-container-image-name nginx \
  2>/dev/null || echo "Backend app already exists"

az webapp create \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --plan clipshare-plan \
  --deployment-container-image-name nginx \
  2>/dev/null || echo "Frontend app already exists"

# Get credentials
echo "🔑 Getting credentials..."
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name $COSMOS_DB \
  --resource-group $RESOURCE_GROUP \
  --query documentEndpoint -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name $COSMOS_DB \
  --resource-group $RESOURCE_GROUP \
  --query primaryMasterKey -o tsv)

ACR_USERNAME=$(az acr credential show \
  --name $ACR_NAME \
  --query username -o tsv)

ACR_PASSWORD=$(az acr credential show \
  --name $ACR_NAME \
  --query passwords[0].value -o tsv)

ACR_LOGIN_SERVER=$(az acr show \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP \
  --query loginServer -o tsv)

# Build and push images
echo "🔨 Building Docker images..."
echo "   This may take a few minutes..."

az acr login --name $ACR_NAME

echo "   Building backend..."
docker build -f docker/Dockerfile.backend \
  -t $ACR_LOGIN_SERVER/clipshare-backend:latest . \
  || { echo "❌ Backend build failed"; exit 1; }

echo "   Building frontend..."
docker build -f docker/Dockerfile.frontend \
  -t $ACR_LOGIN_SERVER/clipshare-frontend:latest . \
  || { echo "❌ Frontend build failed"; exit 1; }

echo "📤 Pushing images to ACR..."
docker push $ACR_LOGIN_SERVER/clipshare-backend:latest || { echo "❌ Backend push failed"; exit 1; }
docker push $ACR_LOGIN_SERVER/clipshare-frontend:latest || { echo "❌ Frontend push failed"; exit 1; }

# Configure backend
echo "⚙️  Configuring backend..."
az webapp config container set \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name $ACR_LOGIN_SERVER/clipshare-backend:latest \
  --docker-registry-server-url https://$ACR_LOGIN_SERVER \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

az webapp config appsettings set \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
    COSMOS_KEY="$COSMOS_KEY" \
    STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION_STRING" \
    PORT=80 \
    FLASK_APP=app.py

# Configure frontend
echo "⚙️  Configuring frontend..."
BACKEND_URL="https://$BACKEND_APP.azurewebsites.net"

az webapp config container set \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name $ACR_LOGIN_SERVER/clipshare-frontend:latest \
  --docker-registry-server-url https://$ACR_LOGIN_SERVER \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

az webapp config appsettings set \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    REACT_APP_API_URL="$BACKEND_URL/api"

# Configure CORS
echo "🔒 Configuring CORS..."
az webapp cors add \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins "https://$FRONTEND_APP.azurewebsites.net" \
  2>/dev/null || echo "CORS already configured"

echo ""
echo "✅ Deployment Complete!"
echo "======================="
echo ""
echo "🌐 Frontend URL: https://$FRONTEND_APP.azurewebsites.net"
echo "🔧 Backend URL:  https://$BACKEND_APP.azurewebsites.net"
echo ""
echo "📋 Next Steps:"
echo "1. Wait 2-3 minutes for containers to start"
echo "2. Test backend: curl https://$BACKEND_APP.azurewebsites.net/api/health"
echo "3. Open frontend in browser: https://$FRONTEND_APP.azurewebsites.net"
echo ""
echo "📊 View resources in Azure Portal:"
echo "   https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP"
echo ""

