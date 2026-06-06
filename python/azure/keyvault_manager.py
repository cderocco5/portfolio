# key_vault_manager.py
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.keyvault.certificates import CertificateClient

# Replace with your Key Vault URL
KEY_VAULT_URL = "https://my-demo-kv.vault.azure.net/"

# Authenticate using DefaultAzureCredential (supports environment, managed identity, etc.)
credential = DefaultAzureCredential()

# Clients for secrets and certificates
secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
certificate_client = CertificateClient(vault_url=KEY_VAULT_URL, credential=credential)


# ----------------- Secret Management -----------------
def set_secret(name: str, value: str):
    """Create or update a secret."""
    secret = secret_client.set_secret(name, value)
    print(f"Secret '{name}' set with value '{value}'.")
    return secret

def get_secret(name: str):
    """Retrieve a secret value."""
    secret = secret_client.get_secret(name)
    print(f"Secret '{name}' has value '{secret.value}'.")
    return secret

def delete_secret(name: str):
    """Delete a secret."""
    poller = secret_client.begin_delete_secret(name)
    deleted_secret = poller.result()
    print(f"Secret '{name}' deleted.")
    return deleted_secret


# ----------------- Certificate Management -----------------
def create_certificate(name: str, policy=None):
    """Create a certificate. Optionally provide a policy dictionary."""
    cert_operation = certificate_client.begin_create_certificate(name, policy)
    cert = cert_operation.result()
    print(f"Certificate '{name}' created.")
    return cert

def get_certificate(name: str):
    """Retrieve a certificate."""
    cert = certificate_client.get_certificate(name)
    print(f"Certificate '{name}' retrieved.")
    return cert

def delete_certificate(name: str):
    """Delete a certificate."""
    poller = certificate_client.begin_delete_certificate(name)
    deleted_cert = poller.result()
    print(f"Certificate '{name}' deleted.")
    return deleted_cert


# ----------------- Example Usage -----------------
if __name__ == "__main__":
    # Secrets
    set_secret("mySecret", "SuperSecretValue")
    get_secret("mySecret")
    delete_secret("mySecret")

    # Certificates
    create_certificate("myCert")
    get_certificate("myCert")
    delete_certificate("myCert")