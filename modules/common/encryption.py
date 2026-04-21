from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from io import BytesIO
import requests
from app.logger import logger
from app.config import cfg


class AESCipher:
    """AES加解密工具 (参考 split/consistency_process/encryption_decryption.py)"""

    def __init__(self, key=None, iv=None):
        """
        初始化

        Args:
            key: 密钥 (16字节), 默认从配置读取
            iv: 初始向量 (16字节), 默认从配置读取
        """
        if key is None:
            key = cfg.EncryptionDecryptionKey['secret_key']
        if iv is None:
            iv = cfg.EncryptionDecryptionKey['iv']

        if isinstance(key, str):
            key = key.encode()
        if isinstance(iv, str):
            iv = iv.encode()

        self.key = key
        self.iv = iv

    def encrypt_text(self, plain_text):
        """
        加密文本

        Args:
            plain_text: 明文

        Returns:
            str: Base64编码的密文
        """
        import base64
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        padded_text = pad(plain_text.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_text)
        return base64.b64encode(self.iv + encrypted).decode('utf-8')

    def decrypt_text(self, encrypted_text):
        """
        解密文本

        Args:
            encrypted_text: Base64编码的密文

        Returns:
            str: 明文
        """
        import base64
        encrypted_bytes = base64.b64decode(encrypted_text)
        # 提取IV (前16字节)
        iv = encrypted_bytes[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted_bytes[AES.block_size:]), AES.block_size)
        return decrypted.decode('utf-8')

    def decrypt_s3_content(self, s3_url):
        """
        解密S3内容

        Args:
            s3_url: S3文件URL

        Returns:
            BytesIO: 解密后的内容流
        """
        try:
            response = requests.get(
                s3_url,
                proxies={'https': '', 'http': ''},
                verify=False,
                timeout=60
            )
            response.raise_for_status()
            encrypted_content = response.content

            # 提取IV (前16字节)
            iv = encrypted_content[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(encrypted_content[AES.block_size:]), AES.block_size)

            return BytesIO(decrypted)

        except Exception as e:
            logger.error("解密S3内容失败: {}".format(e))
            raise


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
