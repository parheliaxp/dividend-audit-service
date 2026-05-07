from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from app.config import cfg


class AESCipher:
    """AES加解密工具"""

    def __init__(self, key=None):
        """
        初始化

        Args:
            key: 密钥 (16字节), 默认从配置读取
        """
        if key is None:
            key = cfg.EncryptionDecryptionKey['secret_key']
        if isinstance(key, str):
            key = key.encode()
        self.key = key

    def encrypt_text(self, plain_text):
        """加密文本"""
        from os import urandom
        iv = urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()

        encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
        return b64encode(iv + encrypted_bytes).decode('utf-8')

    def decrypt_text(self, encrypted_text):
        """
        解密文本

        Args:
            encrypted_text: Base64编码的密文

        Returns:
            str: 明文
        """
        decoded_data = b64decode(encrypted_text)
        iv = decoded_data[:16]
        encrypted_data = decoded_data[16:]

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()

        return decrypted_data.decode('utf-8')


# 全局便捷函数
_cipher = None


def get_cipher():
    """获取全局AES cipher实例"""
    global _cipher
    if _cipher is None:
        _cipher = AESCipher()
    return _cipher


def decrypt_text(text):
    """便捷解密函数"""
    return get_cipher().decrypt_text(text)


def encrypt_text(text):
    """便捷加密函数"""
    return get_cipher().encrypt_text(text)
