"""Simple encryption utility for sensitive data like email passwords."""

import base64
import hashlib
from cryptography.fernet import Fernet
from app.core.config import settings


def _derive_key() -> bytes:
    """Derive a Fernet key from the JWT secret."""
    key = hashlib.sha256(settings.JWT_SECRET.encode()).digest()
    return base64.urlsafe_b64encode(key)


_fernet = Fernet(_derive_key())


def encrypt(plain_text: str) -> str:
    """Encrypt a string and return base64-encoded ciphertext."""
    return _fernet.encrypt(plain_text.encode()).decode()


def decrypt(cipher_text: str) -> str:
    """Decrypt a base64-encoded ciphertext and return the original string."""
    return _fernet.decrypt(cipher_text.encode()).decode()
