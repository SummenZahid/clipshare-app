# GitHub Secrets Setup (Optional for CI/CD)

The CI/CD pipeline will skip Docker build/push steps if ACR secrets are not set. This is fine for now.

## If You Want to Enable Full CI/CD Later

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

Add these secrets (only if you have Azure Container Registry):

1. **ACR_REGISTRY**: `your-acr-name.azurecr.io`
2. **ACR_USERNAME**: ACR admin username
3. **ACR_PASSWORD**: ACR admin password
4. **AZURE_CREDENTIALS**: Service principal JSON (for deployment)
5. **AZURE_WEBAPP_NAME**: Your backend web app name
6. **AZURE_WEBAPP_NAME_STAGING**: Staging web app name (optional)

## For Now

The workflow will:
- ✅ Run tests (backend and frontend)
- ✅ Build frontend
- ⏭️ Skip Docker builds (until ACR secrets are added)
- ⏭️ Skip deployments (until Azure credentials are added)

This is fine! You can deploy manually via Azure Portal.

