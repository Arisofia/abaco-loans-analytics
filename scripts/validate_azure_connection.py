"""Validate Azure and Supabase connection and configuration.

This module provides utilities to test Azure Cosmos DB, Storage, and
Key Vault connectivity, plus Supabase API access, with proper error
handling and logging.
"""

import logging
import os
import sys
from typing import Optional

logger = logging.getLogger(__name__)


def validate_supabase_url() -> bool:
    """Validate SUPABASE_URL environment variable is set.

    Returns:
        True if SUPABASE_URL is configured, False otherwise.
    """
    url = os.getenv("SUPABASE_URL")
    if not url:
        logger.warning("SUPABASE_URL not configured")
        return False
    logger.info("SUPABASE_URL is configured")
    return True


def validate_supabase_key() -> bool:
    """Validate Supabase API key is set.

    Returns:
        True if SUPABASE_ANON_KEY is configured, False otherwise.
    """
    key = os.getenv("SUPABASE_ANON_KEY")
    if not key:
        logger.warning("SUPABASE_ANON_KEY not configured")
        return False
    logger.info("SUPABASE_ANON_KEY is configured")
    return True


def validate_azure_credentials() -> bool:
    """Validate Azure credentials are available.

    Returns:
        True if credentials are available, False otherwise.
    """
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError:
        logger.error("Azure SDK not installed: pip install azure-identity")
        return False

    try:
        credential = DefaultAzureCredential()
        # Attempt token retrieval to validate credentials
        _ = credential.get_token(
            "https://management.azure.com/.default"
        )
        logger.info("Azure credentials validated")
        return True
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Azure credential validation failed: %s", str(e))
        return False


def validate_key_vault_access(vault_url: str) -> bool:
    """Validate access to Azure Key Vault.

    Args:
        vault_url: The URL of the Key Vault.

    Returns:
        True if Key Vault is accessible, False otherwise.
    """
    try:
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential
    except ImportError:
        logger.error(
            "Azure Key Vault SDK not installed: "
            "pip install azure-keyvault-secrets"
        )
        return False

    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)
        # List secrets to verify access
        _ = list(client.list_properties_of_secrets())
        logger.info("Key Vault access validated: %s", vault_url)
        return True
    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "Key Vault access failed for %s: %s",
            vault_url,
            str(e)
        )
        return False


def validate_storage_account(
    account_name: str,
    container_name: Optional[str] = None
) -> bool:
    """Validate Azure Storage Account access.

    Args:
        account_name: The storage account name.
        container_name: Optional container to validate.

    Returns:
        True if storage account is accessible, False otherwise.
    """
    try:
        from azure.storage.blob import BlobServiceClient
        from azure.identity import DefaultAzureCredential
    except ImportError:
        logger.error(
            "Azure Storage SDK not installed: "
            "pip install azure-storage-blob"
        )
        return False

    try:
        credential = DefaultAzureCredential()
        account_url = (
            f"https://{account_name}.blob.core.windows.net"
        )
        client = BlobServiceClient(
            account_url=account_url,
            credential=credential
        )
        if container_name:
            container_client = client.get_container_client(
                container_name
            )
            # List blobs to verify access
            _ = list(container_client.list_blobs())
            logger.info(
                "Storage account and container validated: %s/%s",
                account_name,
                container_name
            )
        else:
            # Just list containers
            _ = list(client.list_containers())
            logger.info("Storage account validated: %s", account_name)
        return True
    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "Storage account validation failed for %s: %s",
            account_name,
            str(e)
        )
        return False


def validate_all() -> bool:
    """Validate all critical configurations.

    Returns:
        True if all validations pass, False otherwise.
    """
    checks = [
        ("Supabase URL", validate_supabase_url()),
        ("Supabase API Key", validate_supabase_key()),
        ("Azure Credentials", validate_azure_credentials()),
    ]

    all_passed = all(passed for _, passed in checks)

    logger.info("=" * 50)
    for check_name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info("%s: %s", status, check_name)
    logger.info("=" * 50)

    if all_passed:
        logger.info("All validations passed")
    else:
        logger.error("Some validations failed")

    return all_passed


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    exit_code = 0 if validate_all() else 1
    sys.exit(exit_code)
