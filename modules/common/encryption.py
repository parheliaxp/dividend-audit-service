from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from io import BytesIO
import requests
from app.logger import logger

class AESCipher:
    """AES 加解密工具"""

    def __init__(self, key, iv):
        """
        初始化

        Args:
            key: 密钥 (16字节)
            iv: 初始向量 (16字节)
        """
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
            bytes: 密文
        """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        padded_text = pad(plain_text.encode('utf-8'), AES.block_size)
        return cipher.encrypt(padded_text)

    def decrypt_text(self, encrypted_text):
        """
        解密文本

        Args:
            encrypted_text: 密文

        Returns:
            str: 明文
        """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted = unpad(cipher.decrypt(encrypted_text), AES.block_size)
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

            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decrypted = unpad(cipher.decrypt(encrypted_content), AES.block_size)

            return BytesIO(decrypted)

        except Exception as e:
            logger.error("解密S3内容失败: {}".format(e))
            raise
