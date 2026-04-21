import requests
from app.logger import logger
from app.config import cfg
from modules.common.db_client import exec_query_df, exec_query_raw
from modules.common.encryption import AESCipher
from .text_condenser import TextCondenser
from .llm_auditor import DividendAuditor
from .db_writer import DividendDBWriter


class DividendProcessor:
    """分红审核处理器"""

    def __init__(self):
        self.condenser = TextCondenser()
        self.auditor = DividendAuditor()
        self.db_writer = DividendDBWriter()
        # 使用配置中的密钥
        self._cipher = AESCipher(
            cfg.EncryptionDecryptionKey['secret_key'],
            cfg.EncryptionDecryptionKey['iv']
        )

    def process(self, args):
        """
        主处理流程

        Args:
            args: 请求参数
                - doc_id: 文档ID
                - callback_url: 回调URL

        Returns:
            list: 审核结果列表
        """
        doc_id = args.get("doc_id")
        callback_url = args.get("callback_url")

        logger.info("开始处理 doc_id: {}".format(doc_id))

        # Step 1: 从数据库获取文档chunk
        chunks = self._get_chunks(doc_id)
        if not chunks:
            return self._error_result("文档不存在或内容为空", doc_id)

        logger.info("doc_id: {} 获取chunk数: {}".format(doc_id, len(chunks)))

        # Step 2: 文本浓缩 (筛选包含分红关键词的段落)
        condensed_text = self.condenser.condense(chunks)
        if not condensed_text:
            logger.info("doc_id: {} 未找到分红相关内容".format(doc_id))
            return []

        logger.info("doc_id: {} 浓缩后文本长度: {}".format(doc_id, len(condensed_text)))

        # Step 3: LLM审核
        audit_result = self.auditor.audit(condensed_text, doc_id)

        # Step 4: 结果入库
        try:
            self.db_writer.save(doc_id, audit_result)
        except Exception as e:
            logger.error("结果入库失败: {}".format(e))

        # Step 5: 回调通知
        if callback_url:
            self._callback(callback_url, doc_id, audit_result)

        logger.info("doc_id: {} 处理完成, 发现问题数: {}".format(doc_id, len(audit_result)))

        return audit_result

    def _is_encoded(self, doc_id):
        """
        查询文档是否加密 (参考 split/consistency_process/consistency_sql_reader.py)

        Args:
            doc_id: 文档ID

        Returns:
            bool: 是否加密
        """
        sql = "SELECT encrypt FROM ib_analysis_document WHERE doc_id = {}".format(doc_id)
        try:
            result = exec_query_raw(sql)
            if not result or len(result) == 0:
                return False
            return True if int(result[0][0]) == 1 else False
        except Exception as e:
            logger.warning("doc_id: {} 查询加密状态失败: {}".format(doc_id, e))
            return False

    def _get_chunks(self, doc_id):
        """
        从数据库获取文档chunk (参考 split/consistency_process/consistency_sql_reader.py)

        Args:
            doc_id: 文档ID

        Returns:
            list: chunk列表 [{'id', 'paraid', 'chunkid', 'text', 'flag', 'title', 'metadata'}, ...]
        """
        # 查询是否加密
        is_encrypted = self._is_encoded(doc_id)

        # 查询chunk数据
        sql = """
            SELECT id, paraid, chunkid, text, flag, title, metadata
            FROM analysis_doc_chunk_info_ib
            WHERE doc_id = {} AND audit_type = 2
            ORDER BY id
        """.format(doc_id)

        try:
            df = exec_query_df(sql)
            if df.empty:
                logger.warning("doc_id: {} 未找到chunk数据".format(doc_id))
                return []

            chunks = []
            for _, row in df.iterrows():
                text = row['text']

                # 根据加密状态决定是否解密
                if is_encrypted:
                    try:
                        text = self._cipher.decrypt_text(text)
                    except Exception as e:
                        logger.warning("chunk id={} 解密失败: {}".format(row['id'], e))

                chunks.append({
                    'id': row['id'],
                    'paraid': row['paraid'] if 'paraid' in row else '',
                    'chunkid': row['chunkid'] if 'chunkid' in row else '',
                    'text': text,
                    'flag': row['flag'] if 'flag' in row else '',
                    'title': row['title'] if 'title' in row else '',
                    'metadata': row['metadata'] if 'metadata' in row else ''
                })

            return chunks

        except Exception as e:
            logger.error("查询chunk失败: {}".format(e))
            return []

    def _callback(self, url, doc_id, result):
        """回调通知"""
        try:
            response = requests.post(
                url,
                json={
                    'doc_id': doc_id,
                    'status': 'completed',
                    'result_count': len(result),
                    'has_error': len(result) > 0
                },
                timeout=10
            )
            logger.info("回调成功: {}".format(url))
        except Exception as e:
            logger.warning("回调失败: {}".format(e))

    def _error_result(self, message, doc_id=None):
        """返回错误结果"""
        logger.error("doc_id: {}, 错误: {}".format(doc_id, message))
        return [{
            'type': '系统错误',
            'content': message,
            'reason': message,
            'suggestion': '请检查文档或联系管理员',
            'l1_type': '系统错误',
            'l2_type': '分红数据审核'
        }]
