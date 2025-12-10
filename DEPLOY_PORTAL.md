# Deploy via Azure Portal (Recommended for Student Accounts)

Since your student account has region restrictions, deploying via Azure Portal is easier.

## Step 1: Create Cosmos DB

1. Go to https://portal.azure.com
2. Search "Cosmos DB" → Create
3. **Basics:**
   - Subscription: Azure for Students
   - Resource Group: `clipshare-rg` (use existing)
   - Account Name: `clipshare-db-[yourname]` (must be globally unique)
   - API: Core (SQL)
   - Location: **East US** (same as resource group)
   - Capacity: Free tier or 400 RU/s
4. Click "Review + Create" → Create

5. **Create Database:**
   - Go to your Cosmos DB account
   - Data Explorer → New Container
   - Database: `clipsharedb` (create new)
   - Container: `videos`
   - Partition key: `/id`
   - Throughput: 400

## Step 2: Create Storage Account

1. Search "Storage Account" → Create
2. **Basics:**
   - Resource Group: `clipshare-rg`
   - Name: `clipshare[random6digits]` (lowercase, numbers only)
   - Location: **East US**
   - Performance: Standard
   - Redundancy: LRS
3. Create

4. **Create Container:**
   - Go to Storage Account → Containers → + Container
   - Name: `videos`
   - Public access: Blob

## Step 3: Create Container Registry (ACR)

1. Search "Container Registry" → Create
2. **Basics:**
   - Resource Group: `clipshare-rg`
   - Registry name: `clipshareacr[random]` (must be globally unique)
   - Location: **East US**
   - SKU: Basic
   - Admin user: **Enable**
3. Create

## Step 4: Build and Push Docker Images

```bash
# Get ACR login server
ACR_NAME="your-acr-name"
az acr login --name $ACR_NAME

# Build images
docker build -f docker/Dockerfile.backend -t $ACR_NAME.azurecr.io/clipshare-backend:latest .
docker build -f docker/Dockerfile.frontend -t $ACR_NAME.azurecr.io/clipshare-frontend:latest .

# Push
docker push $ACR_NAME.azurecr.io/clipshare-backend:latest
docker push $ACR_NAME.azurecr.io/clipshare-frontend:latest
```

## Step 5: Create App Service Plan

1. Search "App Service Plan" → Create
2. **Basics:**
   - Resource Group: `clipshare-rg`
   - Name: `clipshare-plan`
   - OS: **Linux**
   - Region: **East US**
   - Pricing: Free (F1) or Basic (B1)
3. Create

## Step 6: Create Web Apps

**Backend:**
1. Search "Web App" → Create
2. **Basics:**
   - Resource Group: `clipshare-rg`
   - Name: `clipshare-backend-[yourname]` (globally unique)
   - Publish: **Docker Container**
   - OS: **Linux**
   - App Service Plan: Select `clipshare-plan`
3. **Docker:**
   - Options: Single Container
   - Image Source: Azure Container Registry
   - Registry: Select your ACR
   - Image: `clipshare-backend`
   - Tag: `latest`
4. Create

**Frontend:**
- Repeat with name: `clipshare-frontend-[yourname]`
- Image: `clipshare-frontend`

## Step 7: Configure Backend Settings

1. Go to Backend Web App → Configuration → Application settings
2. Add:
   - `COSMOS_ENDPOINT`: From Cosmos DB → Keys → URI
   - `COSMOS_KEY`: From Cosmos DB → Keys → Primary Key
   - `STORAGE_CONNECTION_STRING`: From Storage Account → Access Keys → Connection string
   - `PORT`: `80`
   - `FLASK_APP`: `app.py`
3. Save

## Step 8: Configure Frontend Settings

1. Go to Frontend Web App → Configuration
2. Add:
   - `REACT_APP_API_URL`: `https://clipshare-backend-[yourname].azurewebsites.net/api`
3. Save

## Step 9: Enable CORS

1. Backend Web App → API → CORS
2. Add allowed origin: `https://clipshare-frontend-[yourname].azurewebsites.net`
3. Save

## Step 10: Test

```bash
# Backend
curl https://clipshare-backend-[yourname].azurewebsites.net/api/health

# Frontend
open https://clipshare-frontend-[yourname].azurewebsites.net
```

## Quick Commands (After Portal Setup)

Get connection strings:
```bash
# Cosmos DB
az cosmosdb show --name YOUR_DB_NAME --resource-group clipshare-rg --query documentEndpoint -o tsv
az cosmosdb keys list --name YOUR_DB_NAME --resource-group clipshare-rg --query primaryMasterKey -o tsv

# Storage
az storage account show-connection-string --name YOUR_STORAGE --resource-group clipshare-rg --query connectionString -o tsv
```

