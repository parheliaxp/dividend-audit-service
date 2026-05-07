import json
from datetime import datetime
from app.logger import logger
from app.config import cfg
from modules.common.db_client import exec_sql, exec_query_df


class DividendDBWriter:
    """分红审核结果数据库写入器"""

    TABLE_NAME = "dividend_audit_result"

    def __init__(self):
        self.env = cfg.env

    def save(self, doc_id, audit_result):
        """
        保存审核结果到数据库

        Args:
            doc_id: 文档ID
            audit_result: 审核结果列表
        """
        try:
            self._ensure_table_exists()

            result_json = json.dumps(audit_result, ensure_ascii=False).replace("'", "''")
            create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status = 1 if audit_result else 0

            sql = """
                INSERT INTO {} (doc_id, status, audit_result, create_time, env)
                VALUES ({}, {}, '{}', '{}', '{}')
            """.format(self.TABLE_NAME, doc_id, status, result_json, create_time, self.env)

            exec_sql(sql)
            logger.info("doc_id: {} 审核结果已入库, status: {}".format(doc_id, status))

        except Exception as e:
            logger.error("保存审核结果失败: {}".format(e))
            raise

    def _ensure_table_exists(self):
        """确保表存在 (Vastbase/PostgreSQL语法)"""
        create_sql = """
            CREATE TABLE IF NOT EXISTS {} (
                id BIGSERIAL PRIMARY KEY,
                doc_id BIGINT NOT NULL,
                status INT DEFAULT 0,
                audit_result TEXT,
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                env VARCHAR(50)
            )
        """.format(self.TABLE_NAME)

        try:
            exec_sql(create_sql)
            # 创建索引
            exec_sql("CREATE INDEX IF NOT EXISTS idx_{}_doc_id ON {} (doc_id)".format(self.TABLE_NAME, self.TABLE_NAME))
        except Exception as e:
            logger.warning("创建表失败(可能已存在): {}".format(e))

    def get_result(self, doc_id):
        """获取审核结果"""
        sql = """
            SELECT * FROM {} WHERE doc_id = {} ORDER BY create_time DESC LIMIT 1
        """.format(self.TABLE_NAME, doc_id)

        try:
            df = exec_query_df(sql)
            if df.empty:
                return None

            row = df.iloc[0]
            return {
                'id': row['id'],
                'doc_id': row['doc_id'],
                'status': row['status'],
                'audit_result': json.loads(row['audit_result']) if row['audit_result'] else [],
                'create_time': str(row['create_time']),
                'env': row['env']
            }
        except Exception as e:
            logger.error("获取审核结果失败: {}".format(e))
            return None


# 全局实例
db_writer = DividendDBWriter()
