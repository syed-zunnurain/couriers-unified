import base64
import os
from cryptography.fernet import Fernet
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Handles encryption and decryption of sensitive data."""
    
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get encryption key from settings or create a new one."""
        # In production, this should be set as an environment variable
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        
        if not key:
            # Generate a new key (only for development)
            key = Fernet.generate_key()
            logger.warning("No ENCRYPTION_KEY found in settings. Generated new key for development.")
            logger.warning("IMPORTANT: Set ENCRYPTION_KEY in production environment!")
        
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext and return base64 encoded string."""
        if not plaintext:
            return ""
        
        try:
            encrypted_bytes = self.cipher.encrypt(plaintext.encode('utf-8'))
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt base64 encoded string and return plaintext."""
        if not encrypted_text:
            return ""
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

# Global instance
encryption_manager = EncryptionManager()
