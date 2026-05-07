"""
Vastbase数据库客户端

参考: /Users/gordangao/zhiyue/split/client_plugin/pg_client.py
"""

import psycopg2
import pandas as pd
from urllib.parse import quote_plus as urlquote
from sqlalchemy import create_engine, text
from retry import retry
from app.logger import logger
from app.config import cfg


class VastbaseClient:
    """Vastbase数据库客户端 (PostgreSQL兼容)"""

    @staticmethod
    def get_connection(db_config=None):
        """获取数据库连接"""
        if db_config is None:
            db_config = cfg.db_config
        params = db_config["vastbase"]
        return psycopg2.connect(
            database=params['db_name'],
            user=params['user'],
            password=params['password'],
            host=params['host'],
            port=params['port']
        )

    def __init__(self, db_config=None):
        if db_config is None:
            db_config = cfg.db_config
        params = db_config["vastbase"]
        url = 'postgresql+psycopg2://{}:{}@{}:{}/{}?client_encoding=utf8'.format(
            params['user'], urlquote(str(params['password'])),
            params['host'], params['port'], params['db_name']
        )
        self.engine = create_engine(
            url,
            pool_recycle=3600,
            pool_size=20,
            pool_pre_ping=True,
            isolation_level="AUTOCOMMIT"
        )
        self.url = url

    @retry(delay=0.5, tries=3)
    def execute(self, sql):
        """执行SQL语句"""
        with self.engine.begin() as conn:
            cursor_res = conn.execute(text(sql))
        return cursor_res

    @retry(delay=0.5, tries=3)
    def query(self, sql):
        """查询返回DataFrame"""
        cursor_res = self.execute(sql)
        result = pd.DataFrame(cursor_res.fetchall(), columns=cursor_res.keys())
        return result

    @retry(delay=0.5, tries=3)
    def read_data(self, sql):
        """读取数据返回列表"""
        cursor_res = self.execute(sql)
        columns = list(cursor_res.keys())
        if len(columns) == 1:
            result = [x[0] for x in cursor_res.fetchall()]
        else:
            result = list(cursor_res.fetchall())
        return result

    def close(self):
        """关闭连接"""
        self.engine.dispose()
        del self.engine


# 全局数据库客户端
_database = None


def get_database():
    """获取全局数据库实例"""
    global _database
    if _database is None:
        _database = VastbaseClient()
    return _database


def exec_query_df(sql):
    """执行查询返回DataFrame"""
    db = get_database()
    return db.query(sql)


def exec_query_raw(sql):
    """
    执行查询返回原生元组列表

    参考: /Users/gordangao/zhiyue/split/client_plugin/pg_client.py exec_query_by_pymysql_raw
    """
    connection = VastbaseClient.get_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    res = []
    for row in cursor.fetchall():
        res.append(row)
    cursor.close()
    connection.close()
    return res


def exec_sql(sql_text):
    """
    执行增删改SQL

    参考: /Users/gordangao/zhiyue/split/client_plugin/pg_client.py exec_sql_by_pymysql
    """
    connection = VastbaseClient.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(sql_text)
        connection.commit()
    except Exception as ex:
        logger.error(ex)
        logger.error(sql_text)
    finally:
        cursor.close()
        connection.close()


def exec_sql_with_rowcount(sql_text):
    """执行增删改SQL并返回影响行数"""
    update_flag = 0
    connection = VastbaseClient.get_connection()
    cursor = connection.cursor()
    cursor.execute(sql_text)

    if cursor.rowcount > 0:
        update_flag = 1

    connection.commit()
    cursor.close()
    connection.close()
    return update_flag


def get_dividend_chunks(doc_id):
    """
    获取分红审核的文档chunk数据

    参考: /Users/gordangao/zhiyue/split/consistency_process/consistency_sql_reader.py sql_query

    Args:
        doc_id: 文档ID

    Returns:
        list: chunk列表 [{'id', 'paraid', 'chunkid', 'text', 'flag', 'title', 'metadata'}, ...]
    """
    from modules.common.encryption import AESCipher

    cipher = AESCipher()

    sql = """
        SELECT id, paraid, chunkid, text, flag, title, metadata
        FROM analysis_doc_chunk_info_ib
        WHERE doc_id = {} AND audit_type = 7
        ORDER BY id
    """.format(doc_id)

    try:
        sql_res = exec_query_raw(sql)
        if not sql_res:
            logger.warning("doc_id: {} 未找到chunk数据".format(doc_id))
            return []

        chunks = []
        for row in sql_res:
            # 解密
            try:
                text = cipher.decrypt_text(row[3])
            except Exception as e:
                logger.warning("chunk id={} 解密失败: {}".format(row[0], e))
                text = row[3]

            chunks.append({
                'id': row[0],
                'paraid': row[1] if row[1] else '',
                'chunkid': row[2] if row[2] else '',
                'text': text,
                'flag': row[4] if row[4] else '',
                'title': row[5] if row[5] else '',
                'metadata': row[6] if row[6] else ''
            })

        return chunks

    except Exception as e:
        logger.error("查询chunk失败: {}".format(e))
        return []
