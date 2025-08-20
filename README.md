# Azure Functions Deployment Guide

## Overview

Your weather alert system is now **serverless** and ready for Azure Functions deployment. Here's how it works:

### **Serverless Architecture:**
- **Timer Trigger**: Runs every hour automatically (no server maintenance)
- **HTTP Endpoints**: For testing and status checks
- **Azure Table Storage**: Replaces SQLite for cloud storage
- **Pay-per-execution**: Only pay when functions run

## Deployment Steps

### 1. Prerequisites

Install Azure Functions Core Tools:
```bash
# macOS
brew tap azure/functions
brew install azure-functions-core-tools@4

# Or via npm
npm install -g azure-functions-core-tools@4
```

Install Azure CLI:
```bash
# macOS
brew install azure-cli

# Login to Azure
az login
```

### 2. Create Azure Resources

```bash
# Set variables
RESOURCE_GROUP="weather-alerts-rg"
STORAGE_ACCOUNT="weatheralertstorage$(date +%s)"
FUNCTION_APP="weather-alerts-func-$(date +%s)"
LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Create function app
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name $FUNCTION_APP \
  --storage-account $STORAGE_ACCOUNT \
  --os-type Linux
```

### 3. Configure Application Settings

```bash
# Set environment variables in Azure
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "OPENWEATHER_API_KEY=your_api_key_here" \
    "EMAIL_ADDRESS=your_email@gmail.com" \
    "EMAIL_APP_PASSWORD=your_app_password" \
    "RECIPIENT_EMAIL=alerts@yourdomain.com" \
    "AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --query connectionString --output tsv)"
```

### 4. Deploy the Function

```bash
# Deploy from your project directory
func azure functionapp publish $FUNCTION_APP
```

## Function Endpoints

After deployment, you'll have these endpoints:

### **Timer Trigger** (Automatic)
- Runs every hour at minute 0
- Checks weather and sends alerts
- No manual intervention needed

### **HTTP Endpoints**

**Status Check:**
```
GET https://your-function-app.azurewebsites.net/api/weather/status?code=your_function_key
```

**Manual Test:**
```
GET https://your-function-app.azurewebsites.net/api/weather/test?code=your_function_key
```

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements-azure.txt
```

### 2. Configure Local Settings
Edit `local.settings.json` with your API keys.

### 3. Run Locally
```bash
func start
```

### 4. Test Endpoints
```bash
# Test the weather check
curl http://localhost:7071/api/weather/test

# Check status
curl http://localhost:7071/api/weather/status
```

## Azure Storage Tables

Your data is stored in Azure Table Storage:

- **WeatherHistory**: Hourly weather data for all cities
- **AlertsHistory**: All triggered alerts with details

## Monitoring

### View Logs
```bash
# Stream live logs
func azure functionapp logstream $FUNCTION_APP
```

### Azure Portal
1. Go to [portal.azure.com](https://portal.azure.com)
2. Navigate to your Function App
3. Check "Functions" → "weather_alert_timer" → "Monitor"

## Cost Estimation

**Azure Functions Consumption Plan:**
- First 1M executions: Free
- Additional executions: $0.20 per million
- Memory usage: $0.000016/GB-s

**Azure Table Storage:**
- First 100GB: $0.045/GB/month
- Transactions: $0.00036 per 10K

**Estimated Monthly Cost: < $1**

## Troubleshooting

### Common Issues

1. **Function not triggering**: Check timer expression in `function_app.py`
2. **Storage errors**: Verify connection string in app settings
3. **Email not sending**: Check Gmail app password configuration

### Debug Commands
```bash
# Check function app settings
az functionapp config appsettings list --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

# View function logs
az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
```

## Security

- Function keys protect HTTP endpoints
- Storage connection strings are encrypted
- Email credentials stored as app settings (encrypted)

## Scaling

Azure Functions automatically scale based on demand:
- **Timer trigger**: Runs exactly once per hour
- **HTTP endpoints**: Scale up during high traffic
- **No server management**: Azure handles everything
