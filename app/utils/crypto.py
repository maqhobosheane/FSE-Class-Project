from cryptography.fernet import Fernet
from config import config

# Initialize Fernet with the key from config
cipher_suite = Fernet(config.ENCRYPTION_KEY.encode())

def encrypt_seed(seed: str) -> str:
    """
    Encrypts the wallet seed.
    Corresponds to: encrypt(Wallet.seed)
    """
    encrypted_seed = cipher_suite.encrypt(seed.encode())
    return encrypted_seed.decode()

def decrypt_seed(encrypted_seed: str) -> str:
    """Decrypts the wallet seed."""
    decrypted_seed = cipher_suite.decrypt(encrypted_seed.encode())
    return decrypted_seed.decode()