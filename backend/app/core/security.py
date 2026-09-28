import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class SecretCipher:
    def __init__(self, app_secret: str) -> None:
        digest = hashlib.sha256(app_secret.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(digest))

    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        try:
            return self.fernet.decrypt(value.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("Stored provider secret cannot be decrypted") from exc


def get_secret_cipher() -> SecretCipher:
    return SecretCipher(get_settings().app_secret)


def secret_hint(value: str) -> str:
    return f"••••{value[-4:]}" if len(value) >= 4 else "••••"
