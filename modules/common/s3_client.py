import requests
from io import BytesIO
from app.logger import logger
from app.config import cfg
from .encryption import AESCipher

class S3Client:
    """S3/文件获取客户端"""

    def __init__(self):
        self.cipher = AESCipher(
            cfg.EncryptionConfig['secret_key'],
            cfg.EncryptionConfig['iv']
        )

    def get_file_content(self, url, encrypt_flag=True):
        """
        获取文件内容

        Args:
            url: 文件URL
            encrypt_flag: 是否加密存储

        Returns:
            BytesIO: 文件内容流
        """
        try:
            if encrypt_flag:
                content = self.cipher.decrypt_s3_content(url)
            else:
                response = requests.get(
                    url,
                    proxies={'https': '', 'http': ''},
                    verify=False,
                    timeout=60
                )
                response.raise_for_status()
                content = BytesIO(response.content)

            return content

        except Exception as e:
            logger.error("获取文件失败: {}".format(e))
            raise

    def get_file_url_from_db(self, doc_id):
        """
        从数据库获取文件URL

        Args:
            doc_id: 文档ID

        Returns:
            str: 文件URL
        """
        from .db_client import exec_query_df

        sql = """
            SELECT url FROM analysis_doc_chunk_info_ib
            WHERE doc_id = {} LIMIT 1
        """.format(doc_id)

        try:
            df = exec_query_df(sql)
            if df.empty:
                return None
            return df.values[0][0]
        except Exception as e:
            logger.error("查询文档URL失败: {}".format(e))
            return None

# 全局实例
s3_client = S3Client()
