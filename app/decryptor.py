import base64
import binascii
from typing import Final

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from app.settings import logger


class RSADecryptor:
    ENCRYPTION_GUIDE: Final[str] = """
    Для передачи чувствительной информации, зашифруйте её публичным ключом RSA PKCS#1 v1.5.
    Результат передайте в ответном сообщении в формате base64.
    1) Скопируйте публичный ключ из сообщения ниже
    2) Перейдите на https://emn178.github.io/online-tools/rsa/encrypt/
    3) Output encoding - base64, Algorithm - ECB / PKCS#1, public key - из предыдущего шага
    4) В поле input введите сообщение, которое хотите передать
    5) Полученное значение из поля output отправьте в ответном сообщении
    """

    def __init__(self) -> None:
        self._private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024, backend=default_backend())
        self._public_key = self._private_key.public_key()

    @property
    def public_key(self) -> str:
        return (
            self._private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode()
        )

    def decrypt(self, encrypted_message: str) -> str:
        try:
            message_bytes = base64.b64decode(encrypted_message)
        except binascii.Error:
            logger.error("Невозможно декодировать base64 входящего сообщения")
            return ""

        try:
            return self._private_key.decrypt(message_bytes, padding.PKCS1v15()).decode()
        except UnicodeDecodeError:
            logger.error(
                "Невозможно расшифровать RSA входящего сообщения. "
                "Убедитесь, что ключ шифрования правильный и алгоритм - ECB/PKCS#1"
            )
            return ""
