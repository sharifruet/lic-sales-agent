"""Encryption service for sensitive data."""
from cryptography.fernet import Fernet
from app.src.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""
    
    def __init__(self):
        key = settings.encryption_key
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable not set")
        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()
        self.cipher = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt sensitive data."""
        if not plaintext:
            return ""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt sensitive data."""
        if not ciphertext:
            return ""
        return self.cipher.decrypt(ciphertext.encode()).decode()

