#!/bin/bash
# Deploy recommended Azure services for abaco-analytics-dashboard

set -e

SUBSCRIPTION_ID="695e4491-d568-4105-a1e1-8f2baf3b54df"
RESOURCE_GROUP="AI-MultiAgent-Ecosystem-RG"
WEB_APP_NAME="abaco-analytics-dashboard"
LOCATION="eastus"

echo "🚀 Deploying Azure recommended services for $WEB_APP_NAME..."

# 1. Create Application Insights if not exists
echo "📊 Creating Application Insights..."
az monitor app-insights component create \
  --app "abaco-analytics-insights" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --application-type web \
  --retention-time 90 \
  --subscription "$SUBSCRIPTION_ID" || echo "Application Insights already exists"

# 2. Link Application Insights to Web App
echo "🔗 Linking Application Insights to Web App..."
INSIGHTS_KEY=$(az monitor app-insights component show \
  --app "abaco-analytics-insights" \
  --resource-group "$RESOURCE_GROUP" \
  --query "instrumentationKey" \
  -o tsv 2>/dev/null)

if [ -n "$INSIGHTS_KEY" ]; then
  az webapp config appsettings set \
    --name "$WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$INSIGHTS_KEY" \
    --subscription "$SUBSCRIPTION_ID"
fi

# 3. Enable diagnostic logs
echo "📝 Enabling diagnostic logs..."
az monitor diagnostic-settings create \
  --name "abaco-analytics-diagnostics" \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$WEB_APP_NAME" \
  --logs '[{"category": "AppServiceConsoleLogs", "enabled": true}, {"category": "AppServiceHTTPLogs", "enabled": true}]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]' \
  --workspace "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.operationalinsights/workspaces/abaco-logs" \
  --subscription "$SUBSCRIPTION_ID" || echo "Diagnostic settings already configured"

# 4. Create alert for high error rate
echo "🚨 Creating alert for high error rate..."
az monitor metrics alert create \
  --name "abaco-high-error-rate" \
  --resource-group "$RESOURCE_GROUP" \
  --description "Alert when error rate > 5%" \
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$WEB_APP_NAME" \
  --condition "avg http5xx > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 3 \
  --subscription "$SUBSCRIPTION_ID" || echo "Alert already exists"

# 5. Enable Always On to prevent app from being unloaded
echo "⚡ Enabling Always On..."
az webapp config set \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --always-on true \
  --subscription "$SUBSCRIPTION_ID"

# 6. Set HTTP/2 and MinTlsVersion
echo "🔒 Configuring security settings..."
az webapp config set \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --min-tls-version "1.2" \
  --subscription "$SUBSCRIPTION_ID"

echo "✅ Azure services configured successfully!"
echo "📍 Application Insights: https://portal.azure.com/#@jenineferderashotmail014.onmicrosoft.com/resource/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/components/abaco-analytics-insights"
