# Deploy from GitHub to Azure

## Step 1: Initialize Git Repository

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - ClipShare video sharing platform"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com
2. Click **"+"** → **"New repository"**
3. Fill in:
   - **Repository name**: `clipshare-app` (or your choice)
   - **Description**: "Scalable video sharing platform"
   - **Visibility**: Private (recommended) or Public
   - **DO NOT** initialize with README, .gitignore, or license
4. Click **"Create repository"**

## Step 3: Push to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/clipshare-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Create Azure Resources (Portal)

### 4.1 Create Resource Group
1. Portal → **Resource groups** → **Create**
2. Name: `clipshare-rg`
3. Region: **East US**
4. Create

### 4.2 Create Cosmos DB
1. Portal → **"+ Create a resource"** → **Azure Cosmos DB**
2. **API**: Core (SQL)
3. Fill in:
   - Resource Group: `clipshare-rg`
   - Account Name: `clipshare-db-[yourname]`
   - Location: **East US**
   - Apply Free Tier: Yes
4. Create → Wait 3-5 minutes

**Create Database & Container:**
- Go to Cosmos DB → **Data Explorer**
- **New Container**:
  - Database: `clipsharedb` (new)
  - Container: `videos`
  - Partition key: `/id`
  - Throughput: 400

### 4.3 Create Storage Account
1. Portal → **"+ Create a resource"** → **Storage Account**
2. Fill in:
   - Resource Group: `clipshare-rg`
   - Name: `clipshare[6digits]` (lowercase, numbers)
   - Location: **East US**
   - Performance: Standard
   - Redundancy: LRS
3. Create

**Create Container:**
- Storage Account → **Containers** → **+ Container**
- Name: `videos`
- Public access: **Blob**

### 4.4 Create App Service Plan
1. Portal → **"+ Create a resource"** → **App Service Plan**
2. Fill in:
   - Resource Group: `clipshare-rg`
   - Name: `clipshare-plan`
   - OS: **Linux**
   - Region: **East US**
   - Pricing: **Free F1** or Basic B1
3. Create

## Step 5: Create Web Apps with GitHub Deployment

### 5.1 Create Backend Web App

1. Portal → **"+ Create a resource"** → **Web App**

2. **Basics:**
   - Resource Group: `clipshare-rg`
   - Name: `clipshare-backend-[yourname]`
   - Publish: **Code** ✅
   - Runtime stack: **Python 3.11**
   - Operating System: **Linux**
   - Region: **East US**
   - App Service Plan: `clipshare-plan`

3. **Deployment:**
   - **Continuous deployment**: **Enable** ✅
   - Click **"Configure"**
   - **Source**: **GitHub** ✅
   - Authorize Azure to access GitHub (if first time)
   - **Organization**: Your GitHub username
   - **Repository**: `clipshare-app`
   - **Branch**: `main`
   - **Build provider**: **GitHub Actions** ✅
   - **Runtime stack**: **Python 3.11**

4. Click **Review + create** → **Create**

### 5.2 Configure Backend Settings

1. Go to Backend Web App → **Configuration** → **Application settings**

2. Add these settings:

   | Name | Value |
   |------|-------|
   | `COSMOS_ENDPOINT` | From Cosmos DB → Keys → URI |
   | `COSMOS_KEY` | From Cosmos DB → Keys → Primary Key |
   | `STORAGE_CONNECTION_STRING` | From Storage Account → Access Keys → Connection string |
   | `PORT` | `80` |
   | `FLASK_APP` | `app.py` |
   | `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

3. **General settings:**
   - **Startup Command**: `gunicorn --bind 0.0.0.0:80 app:app`

4. Click **Save**

### 5.3 Create Frontend Web App

1. Portal → **"+ Create a resource"** → **Web App**

2. **Basics:**
   - Name: `clipshare-frontend-[yourname]`
   - Publish: **Code**
   - Runtime stack: **Node 20 LTS**
   - OS: **Linux**
   - Plan: `clipshare-plan`
   - Region: **East US**

3. **Deployment:**
   - **Continuous deployment**: **Enable**
   - Source: **GitHub**
   - Repository: `clipshare-app`
   - Branch: `main`
   - Build provider: **GitHub Actions**
   - **Runtime stack**: **Node 20 LTS**

4. Create

### 5.4 Configure Frontend Settings

1. Frontend Web App → **Configuration** → **Application settings**

2. Add:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://clipshare-backend-[yourname].azurewebsites.net/api`

3. **General settings:**
   - **Startup Command**: Leave empty (React build is static)

4. Save

## Step 6: Update GitHub Actions Workflows

Azure will create GitHub Actions workflows automatically. You may need to update them:

### Backend Workflow (`.github/workflows/azure-webapps-python.yml`)

The workflow should build and deploy. If needed, ensure it:
- Installs dependencies: `pip install -r clipshare-backend/requirements.txt`
- Runs from correct directory: `cd clipshare-backend`
- Uses gunicorn to start

### Frontend Workflow (`.github/workflows/azure-webapps-node.yml`)

Should:
- Install: `npm install` in `clipshare-frontend`
- Build: `npm run build`
- Deploy the `build` folder

## Step 7: Enable CORS

1. Backend Web App → **API** → **CORS**
2. Add: `https://clipshare-frontend-[yourname].azurewebsites.net`
3. Save

## Step 8: Test Deployment

After pushing to GitHub, Azure will automatically:
1. Detect the push
2. Run GitHub Actions
3. Build and deploy

**Check deployment:**
- GitHub → **Actions** tab (see workflow runs)
- Azure Portal → Web App → **Deployment Center** (see deployment status)

**Test:**
```bash
# Backend
curl https://clipshare-backend-[yourname].azurewebsites.net/api/health

# Frontend
open https://clipshare-frontend-[yourname].azurewebsites.net
```

## Troubleshooting

- **Build fails**: Check GitHub Actions logs
- **App won't start**: Check Web App → **Log stream**
- **Environment variables**: Verify in Configuration
- **CORS errors**: Check CORS settings

## Quick Commands

```bash
# Push changes (triggers auto-deployment)
git add .
git commit -m "Update code"
git push origin main

# View deployment logs
az webapp log tail --name clipshare-backend-[yourname] --resource-group clipshare-rg
```

