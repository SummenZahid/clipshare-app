# Quick GitHub Setup Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `clipshare-app`
3. Description: "Scalable video sharing platform"
4. Visibility: **Private** (recommended)
5. **DO NOT** check "Add a README file"
6. Click **"Create repository"**

## Step 2: Push Your Code

```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/clipshare-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Deploy from GitHub in Azure Portal

After pushing, follow `DEPLOY_FROM_GITHUB.md` for Azure Portal setup.

The key difference: When creating Web Apps in Azure Portal, select:
- **Publish**: Code (not Docker Container)
- **Continuous deployment**: Enable
- **Source**: GitHub
- Select your repository and branch

Azure will automatically:
- Set up GitHub Actions workflows
- Build and deploy on every push
- Handle both backend (Python) and frontend (Node.js)

## Benefits

✅ No need to build Docker images manually  
✅ Automatic deployment on every git push  
✅ GitHub Actions handles building  
✅ Easy to update - just push to GitHub  

