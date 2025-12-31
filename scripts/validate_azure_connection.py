#!/usr/bin/env python3
"""
Azure Connection Validator and Setup Script
Validates and configures Azure connections for the entire workspace.
"""

import os
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# Initialize tracing early
try:
    from python.azure_tracing import setup_azure_tracing
    logger, tracer = setup_azure_tracing()
    logger.info("Azure tracing initialized for validate_azure_connection")
except (ImportError, Exception) as tracing_err:
    # Fallback to basic logging if tracing setup fails
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.warning("Azure tracing not initialized: %s", tracing_err)


@dataclass
class AzureConfig:
    """Azure configuration holder."""
    subscription_id: Optional[str] = None
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    storage_account_name: Optional[str] = None
    storage_connection_string: Optional[str] = None
    storage_container_name: Optional[str] = "kpi-exports"
    key_vault_url: Optional[str] = None
    webapp_name: Optional[str] = "abaco-analytics-dashboard"
    resource_group: Optional[str] = "AI-MultiAgent-Ecosystem-RG"


def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    if not os.path.exists(env_path):
        logger.warning(f"{env_path} not found. Using environment variables only.")
        return env_vars
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def validate_azure_credentials() -> Tuple[bool, List[str]]:
    """Validate Azure credentials and authentication."""
    issues = []
    
    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resource import ResourceManagementClient
        
        credential = DefaultAzureCredential()
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        
        if not subscription_id:
            issues.append("AZURE_SUBSCRIPTION_ID not set")
            return False, issues
        
        try:
            client = ResourceManagementClient(credential, subscription_id)
            # Try to list resource groups to validate credentials
            list(client.resource_groups.list())
            logger.info("✓ Azure credentials validated successfully")
            return True, []
        except Exception as e:
            issues.append(f"Azure authentication failed: {str(e)}")
            return False, issues
            
    except ImportError as e:
        issues.append(f"Azure SDK not installed: {str(e)}")
        return False, issues


def validate_storage_connection() -> Tuple[bool, List[str]]:
    """Validate Azure Storage connection."""
    issues = []
    
    try:
        from azure.storage.blob import BlobServiceClient
        from azure.identity import DefaultAzureCredential
        
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        
        if connection_string:
            try:
                client = BlobServiceClient.from_connection_string(connection_string)
                client.get_account_information()
                logger.info("✓ Azure Storage connection (connection string) validated")
                return True, []
            except Exception as e:
                issues.append(f"Storage connection string invalid: {str(e)}")
        elif account_name:
            try:
                account_url = f"https://{account_name}.blob.core.windows.net"
                credential = DefaultAzureCredential()
                client = BlobServiceClient(account_url=account_url, credential=credential)
                client.get_account_information()
                logger.info("✓ Azure Storage connection (managed identity) validated")
                return True, []
            except Exception as e:
                issues.append(f"Storage managed identity failed: {str(e)}")
        else:
            issues.append("Neither AZURE_STORAGE_CONNECTION_STRING nor AZURE_STORAGE_ACCOUNT_NAME set")
        
        return False, issues
        
    except ImportError as e:
        issues.append(f"Azure Storage SDK not installed: {str(e)}")
        return False, issues


def validate_key_vault_connection() -> Tuple[bool, List[str]]:
    """Validate Azure Key Vault connection."""
    issues = []
    
    key_vault_url = os.getenv("AZURE_KEY_VAULT_URL")
    if not key_vault_url:
        logger.info("ℹ Azure Key Vault URL not configured (optional)")
        return True, []
    
    try:
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential
        
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_url, credential=credential)
        
        try:
            # Try to list secrets to validate access
            list(client.list_properties_of_secrets())
            logger.info("✓ Azure Key Vault connection validated")
            return True, []
        except Exception as e:
            issues.append(f"Key Vault access failed: {str(e)}")
            return False, issues
            
    except ImportError as e:
        issues.append(f"Azure Key Vault SDK not installed: {str(e)}")
        return False, issues


def check_required_packages() -> Tuple[bool, List[str]]:
    """Check if required Azure packages are installed."""
    required_packages = [
        "azure-identity",
        "azure-storage-blob",
        "azure-keyvault-secrets",
        "azure-mgmt-resource",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "."))
        except ImportError:
            missing.append(package)
    
    if missing:
        return False, [f"Missing packages: {', '.join(missing)}"]
    
    logger.info("✓ All required Azure packages installed")
    return True, []


def generate_setup_script():
    """Generate a script to help with Azure setup."""
    script = """#!/bin/bash
# Azure Setup Script
# This script helps configure Azure resources for abaco-loans-analytics

set -e

echo "Azure Setup for abaco-loans-analytics"
echo "======================================"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Azure CLI not found. Please install: https://learn.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo "Logging in to Azure..."
az login

# Set subscription
echo ""
echo "Select your subscription:"
az account list --output table
read -p "Enter subscription ID: " SUBSCRIPTION_ID
az account set --subscription "$SUBSCRIPTION_ID"

# Get tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)

echo ""
echo "Resource Group: AI-MultiAgent-Ecosystem-RG"
read -p "Press Enter to continue or Ctrl+C to abort..."

# Create or verify resource group
az group create --name AI-MultiAgent-Ecosystem-RG --location eastus

# Create storage account
read -p "Enter storage account name (lowercase, no special chars): " STORAGE_NAME
az storage account create \\
    --name "$STORAGE_NAME" \\
    --resource-group AI-MultiAgent-Ecosystem-RG \\
    --location eastus \\
    --sku Standard_LRS

# Get connection string
CONNECTION_STRING=$(az storage account show-connection-string \\
    --name "$STORAGE_NAME" \\
    --resource-group AI-MultiAgent-Ecosystem-RG \\
    --query connectionString -o tsv)

# Create container
az storage container create \\
    --name kpi-exports \\
    --account-name "$STORAGE_NAME"

# Create Key Vault (optional)
read -p "Create Azure Key Vault? (y/n): " CREATE_KV
if [ "$CREATE_KV" = "y" ]; then
    read -p "Enter Key Vault name: " KV_NAME
    az keyvault create \\
        --name "$KV_NAME" \\
        --resource-group AI-MultiAgent-Ecosystem-RG \\
        --location eastus
    
    KV_URL="https://$KV_NAME.vault.azure.net/"
else
    KV_URL=""
fi

# Generate .env file
echo ""
echo "Generating .env file..."
cat > .env << EOF
# Azure Configuration
AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID
AZURE_TENANT_ID=$TENANT_ID
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=

# Azure Storage
AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_NAME
AZURE_STORAGE_CONNECTION_STRING=$CONNECTION_STRING
AZURE_STORAGE_CONTAINER_NAME=kpi-exports

# Azure Key Vault
AZURE_KEY_VAULT_URL=$KV_URL

# Azure App Service
AZURE_WEBAPP_NAME=abaco-analytics-dashboard
AZURE_RESOURCE_GROUP=AI-MultiAgent-Ecosystem-RG
EOF

echo ""
echo "✓ Setup complete!"
echo "✓ .env file created with Azure configuration"
echo ""
echo "Next steps:"
echo "1. Review and update .env with additional credentials"
echo "2. Run: python scripts/validate_azure_connection.py"
echo "3. Configure service principal if needed for CI/CD"
"""
    
    with open("scripts/setup_azure.sh", "w") as f:
        f.write(script)
    
    os.chmod("scripts/setup_azure.sh", 0o755)
    logger.info("✓ Generated setup_azure.sh script")


def main():
    """Main validation function."""
    logger.info("Azure Connection Validator")
    logger.info("=" * 50)
    
    # Load environment variables
    env_file = ".env"
    if os.path.exists(env_file):
        env_vars = load_env_file(env_file)
        for key, value in env_vars.items():
            if value and key not in os.environ:
                os.environ[key] = value
        logger.info(f"✓ Loaded {len(env_vars)} variables from {env_file}")
    else:
        logger.warning("No .env file found. Copy .env.example to .env and configure.")
    
    # Run validations
    all_passed = True
    
    logger.info("\n1. Checking required packages...")
    passed, issues = check_required_packages()
    if not passed:
        logger.error("✗ Package check failed:")
        for issue in issues:
            logger.error(f"  - {issue}")
        logger.info("\nInstall missing packages:")
        logger.info("  pip install azure-identity azure-storage-blob azure-keyvault-secrets azure-mgmt-resource")
        all_passed = False
    
    logger.info("\n2. Validating Azure credentials...")
    passed, issues = validate_azure_credentials()
    if not passed:
        logger.error("✗ Credential validation failed:")
        for issue in issues:
            logger.error(f"  - {issue}")
        all_passed = False
    
    logger.info("\n3. Validating Azure Storage connection...")
    passed, issues = validate_storage_connection()
    if not passed:
        logger.error("✗ Storage validation failed:")
        for issue in issues:
            logger.error(f"  - {issue}")
        all_passed = False
    
    logger.info("\n4. Validating Azure Key Vault connection...")
    passed, issues = validate_key_vault_connection()
    if not passed:
        logger.error("✗ Key Vault validation failed:")
        for issue in issues:
            logger.error(f"  - {issue}")
        all_passed = False
    
    # Generate setup script if needed
    if not os.path.exists("scripts/setup_azure.sh"):
        logger.info("\n5. Generating setup script...")
        generate_setup_script()
    
    # Summary
    logger.info("\n" + "=" * 50)
    if all_passed:
        logger.info("✓ All Azure connections validated successfully!")
        return 0
    else:
        logger.error("✗ Some validations failed. Please review the errors above.")
        logger.info("\nSetup help:")
        logger.info("  1. Run: bash scripts/setup_azure.sh")
        logger.info("  2. Or manually configure .env from .env.example")
        return 1


if __name__ == "__main__":
    sys.exit(main())
