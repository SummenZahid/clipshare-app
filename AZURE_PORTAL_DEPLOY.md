# Azure Portal Deployment - Step by Step

## Prerequisites
- Azure account logged in at https://portal.azure.com
- Docker images built locally (we'll do this)

## Step 1: Build Docker Images Locally

```bash
# Build backend
docker build -f docker/Dockerfile.backend -t clipshare-backend:latest .

# Build frontend  
docker build -f docker/Dockerfile.frontend -t clipshare-frontend:latest .

# Test locally (optional)
docker-compose -f docker/docker-compose.yml up
```

## Step 2: Create Azure Container Registry (ACR)

1. Go to https://portal.azure.com
2. Click **"+ Create a resource"**
3. Search **"Container Registry"** → Create
4. Fill in:
   - **Subscription**: Azure for Students
   - **Resource Group**: `clipshare-rg` (create new if needed)
   - **Registry name**: `clipshareacr[yourname]` (must be globally unique, lowercase, 5-50 chars)
   - **Location**: **East US**
   - **SKU**: **Basic**
   - **Admin user**: **Enable** ✅
5. Click **Review + create** → **Create**
6. Wait for deployment (1-2 minutes)

## Step 3: Push Images to ACR

```bash
# Login to your ACR
az acr login --name YOUR_ACR_NAME

# Tag images
docker tag clipshare-backend:latest YOUR_ACR_NAME.azurecr.io/clipshare-backend:latest
docker tag clipshare-frontend:latest YOUR_ACR_NAME.azurecr.io/clipshare-frontend:latest

# Push images
docker push YOUR_ACR_NAME.azurecr.io/clipshare-backend:latest
docker push YOUR_ACR_NAME.azurecr.io/clipshare-frontend:latest
```

## Step 4: Create Cosmos DB

1. Portal → **"+ Create a resource"**
2. Search **"Azure Cosmos DB"** → Create
3. **API**: Select **Core (SQL)**
4. Fill in:
   - **Subscription**: Azure for Students
   - **Resource Group**: `clipshare-rg`
   - **Account Name**: `clipshare-db-[yourname]` (globally unique)
   - **Location**: **East US**
   - **Capacity mode**: **Provisioned throughput**
   - **Apply Free Tier Discount**: **Apply** (if available)
5. Click **Review + create** → **Create**
6. Wait for deployment (3-5 minutes)

### Create Database and Container:
1. Go to your Cosmos DB account
2. Click **Data Explorer** (left menu)
3. Click **New Container**
4. Fill in:
   - **Database id**: `clipsharedb` (create new)
   - **Container id**: `videos`
   - **Partition key**: `/id`
   - **Throughput**: `400`
5. Click **OK**

## Step 5: Create Storage Account

1. Portal → **"+ Create a resource"**
2. Search **"Storage Account"** → Create
3. Fill in:
   - **Subscription**: Azure for Students
   - **Resource Group**: `clipshare-rg`
   - **Storage account name**: `clipshare[6randomdigits]` (lowercase, numbers only, globally unique)
   - **Region**: **East US**
   - **Performance**: **Standard**
   - **Redundancy**: **Locally-redundant storage (LRS)**
4. Click **Review + create** → **Create**

### Create Container:
1. Go to your Storage Account
2. Click **Containers** (left menu)
3. Click **+ Container**
4. Name: `videos`
5. Public access level: **Blob**
6. Click **Create**

## Step 6: Create App Service Plan

1. Portal → **"+ Create a resource"**
2. Search **"App Service Plan"** → Create
3. Fill in:
   - **Subscription**: Azure for Students
   - **Resource Group**: `clipshare-rg`
   - **Name**: `clipshare-plan`
   - **Operating System**: **Linux** ✅
   - **Region**: **East US**
   - **Pricing tier**: **Free F1** (or Basic B1 if you have credits)
4. Click **Review + create** → **Create**

## Step 7: Create Backend Web App

1. Portal → **"+ Create a resource"**
2. Search **"Web App"** → Create
3. **Basics tab:**
   - **Subscription**: Azure for Students
   - **Resource Group**: `clipshare-rg`
   - **Name**: `clipshare-backend-[yourname]` (globally unique)
   - **Publish**: **Docker Container** ✅
   - **Operating System**: **Linux**
   - **App Service Plan**: Select `clipshare-plan`
   - **Region**: **East US**

4. **Docker tab:**
   - **Options**: **Single Container**
   - **Image Source**: **Azure Container Registry**
   - **Registry**: Select your ACR
   - **Image**: `clipshare-backend`
   - **Tag**: `latest`

5. Click **Review + create** → **Create**

### Configure Backend Settings:
1. Go to your Backend Web App
2. **Settings** → **Configuration** → **Application settings**
3. Click **+ New application setting** and add:

   | Name | Value |
   |------|-------|
   | `COSMOS_ENDPOINT` | Get from Cosmos DB → Keys → URI |
   | `COSMOS_KEY` | Get from Cosmos DB → Keys → Primary Key |
   | `STORAGE_CONNECTION_STRING` | Get from Storage Account → Access Keys → Connection string |
   | `PORT` | `80` |
   | `FLASK_APP` | `app.py` |

4. Click **Save**

## Step 8: Create Frontend Web App

1. Portal → **"+ Create a resource"**
2. Search **"Web App"** → Create
3. **Basics:**
   - **Name**: `clipshare-frontend-[yourname]`
   - **Publish**: **Docker Container**
   - **OS**: **Linux**
   - **Plan**: `clipshare-plan`
   - **Region**: **East US**

4. **Docker:**
   - **Image Source**: **Azure Container Registry**
   - **Registry**: Your ACR
   - **Image**: `clipshare-frontend`
   - **Tag**: `latest`

5. Create

### Configure Frontend Settings:
1. Go to Frontend Web App → **Configuration**
2. Add application setting:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://clipshare-backend-[yourname].azurewebsites.net/api`
3. Click **Save**

## Step 9: Enable CORS

1. Go to **Backend Web App**
2. **API** → **CORS**
3. Add allowed origin: `https://clipshare-frontend-[yourname].azurewebsites.net`
4. Click **Save**

## Step 10: Get Connection Strings

### Cosmos DB:
1. Go to Cosmos DB account
2. **Settings** → **Keys**
3. Copy:
   - **URI** (for COSMOS_ENDPOINT)
   - **Primary Key** (for COSMOS_KEY)

### Storage Account:
1. Go to Storage Account
2. **Security + networking** → **Access Keys**
3. Copy **Connection string** (for STORAGE_CONNECTION_STRING)

## Step 11: Test Deployment

```bash
# Test backend
curl https://clipshare-backend-[yourname].azurewebsites.net/api/health

# Open frontend in browser
open https://clipshare-frontend-[yourname].azurewebsites.net
```

## Troubleshooting

- **Container won't start**: Check logs in Web App → **Log stream**
- **CORS errors**: Verify CORS settings in backend
- **Database connection fails**: Check environment variables
- **Images not found**: Verify images pushed to ACR

## Quick Reference

**Your URLs:**
- Frontend: `https://clipshare-frontend-[yourname].azurewebsites.net`
- Backend: `https://clipshare-backend-[yourname].azurewebsites.net`
- Backend API: `https://clipshare-backend-[yourname].azurewebsites.net/api`

**View Logs:**
- Web App → **Monitoring** → **Log stream**

