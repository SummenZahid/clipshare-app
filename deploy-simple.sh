#!/bin/bash
set -e

RESOURCE_GROUP="clipshare-rg"
LOCATION="eastus"

echo "🚀 ClipShare Deployment"
echo "======================="

echo "📦 Using existing resource group: $RESOURCE_GROUP"

echo "🗄️  Creating Cosmos DB..."
DB_NAME="clipshare-db-$(whoami | tr -d '-' | tr '[:upper:]' '[:lower:]' | cut -c1-10)$(date +%s | tail -c 3)"
echo "DB Name: $DB_NAME"

az cosmosdb create \
  --name $DB_NAME \
  --resource-group $RESOURCE_GROUP \
  --default-consistency-level Session \
  --locations regionName=$LOCATION failoverPriority=0 || echo "Cosmos DB creation failed or exists"

echo "📊 Creating database and container..."
az cosmosdb sql database create \
  --account-name $DB_NAME \
  --resource-group $RESOURCE_GROUP \
  --name clipsharedb || echo "Database exists"

az cosmosdb sql container create \
  --account-name $DB_NAME \
  --resource-group $RESOURCE_GROUP \
  --database-name clipsharedb \
  --name videos \
  --partition-key-path "/id" \
  --throughput 400 || echo "Container exists"

echo "✅ Cosmos DB setup complete!"
echo ""
echo "Next: Create Storage Account and ACR via Azure Portal"
echo "Or continue with: az storage account create ..."

