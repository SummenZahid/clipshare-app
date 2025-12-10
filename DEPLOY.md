# Quick Deployment Guide

## Step 1: Create Resource Group

```bash
az group create --name clipshare-rg --location northeurope
```

## Step 2: Create Cosmos DB

```bash
az cosmosdb create \
  --name clipshare-db-$(date +%s | tail -c 4) \
  --resource-group clipshare-rg \
  --default-consistency-level Session \
  --locations regionName=northeurope failoverPriority=0

# Create database and container
az cosmosdb sql database create \
  --account-name clipshare-db-$(date +%s | tail -c 4) \
  --resource-group clipshare-rg \
  --name clipsharedb

az cosmosdb sql container create \
  --account-name clipshare-db-$(date +%s | tail -c 4) \
  --resource-group clipshare-rg \
  --database-name clipsharedb \
  --name videos \
  --partition-key-path "/id" \
  --throughput 400
```

## Step 3: Create Storage Account

```bash
az storage account create \
  --name clipshare$(date +%s | tail -c 6) \
  --resource-group clipshare-rg \
  --location northeurope \
  --sku Standard_LRS \
  --kind StorageV2
```

## Step 4: Create Container Registry

```bash
az acr create \
  --name clipshareacr$(date +%s | tail -c 4) \
  --resource-group clipshare-rg \
  --sku Basic \
  --admin-enabled true \
  --location northeurope
```

## Step 5: Build and Push Images

```bash
# Login to ACR
ACR_NAME="your-acr-name"
az acr login --name $ACR_NAME

# Build and push
docker build -f docker/Dockerfile.backend -t $ACR_NAME.azurecr.io/clipshare-backend:latest .
docker build -f docker/Dockerfile.frontend -t $ACR_NAME.azurecr.io/clipshare-frontend:latest .

docker push $ACR_NAME.azurecr.io/clipshare-backend:latest
docker push $ACR_NAME.azurecr.io/clipshare-frontend:latest
```

## Step 6: Create App Services

```bash
# App Service Plan
az appservice plan create \
  --name clipshare-plan \
  --resource-group clipshare-rg \
  --sku B1 \
  --is-linux \
  --location northeurope

# Backend Web App
az webapp create \
  --name clipshare-backend-$(whoami) \
  --resource-group clipshare-rg \
  --plan clipshare-plan \
  --deployment-container-image-name nginx

# Frontend Web App
az webapp create \
  --name clipshare-frontend-$(whoami) \
  --resource-group clipshare-rg \
  --plan clipshare-plan \
  --deployment-container-image-name nginx
```

## Step 7: Configure Apps

Get your connection strings first:

```bash
COSMOS_ENDPOINT=$(az cosmosdb show --name YOUR_DB_NAME --resource-group clipshare-rg --query documentEndpoint -o tsv)
COSMOS_KEY=$(az cosmosdb keys list --name YOUR_DB_NAME --resource-group clipshare-rg --query primaryMasterKey -o tsv)
STORAGE_CONN=$(az storage account show-connection-string --name YOUR_STORAGE --resource-group clipshare-rg --query connectionString -o tsv)
```

Then configure:

```bash
# Backend settings
az webapp config container set \
  --name clipshare-backend-$(whoami) \
  --resource-group clipshare-rg \
  --docker-custom-image-name YOUR_ACR.azurecr.io/clipshare-backend:latest \
  --docker-registry-server-url https://YOUR_ACR.azurecr.io \
  --docker-registry-server-user $(az acr credential show --name YOUR_ACR --query username -o tsv) \
  --docker-registry-server-password $(az acr credential show --name YOUR_ACR --query passwords[0].value -o tsv)

az webapp config appsettings set \
  --name clipshare-backend-$(whoami) \
  --resource-group clipshare-rg \
  --settings COSMOS_ENDPOINT="$COSMOS_ENDPOINT" COSMOS_KEY="$COSMOS_KEY" STORAGE_CONNECTION_STRING="$STORAGE_CONN" PORT=80
```

## Or Use the Automated Script

```bash
./deploy.sh
```

The script is running in the background. Check progress or run manually if needed.

