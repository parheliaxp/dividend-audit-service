import pymysql
import pandas as pd
from urllib.parse import quote_plus as urlquote
from sqlalchemy import create_engine, text
from retry import retry
from app.logger import logger
from app.config import cfg


class MySQLClient:
    """MySQL数据库客户端 (参考 split/client_plugin/mysql_client.py)"""

    @staticmethod
    def get_connection(db_config, database=None):
        """获取数据库连接"""
        params = db_config["mysql"]
        return pymysql.connect(
            host=params['host'],
            port=params['port'],
            db=params['db_name'],
            user=params['user'],
            password=params['password']
        )

    def __init__(self, db_config, database=None):
        params = db_config["mysql"]
        url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
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
        """读取数据"""
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
        _database = MySQLClient(cfg.db_config)
    return _database


def exec_query_df(sql):
    """执行查询返回DataFrame"""
    db = get_database()
    return db.query(sql)


def exec_query_raw(sql):
    """
    执行查询返回原生元组列表 (参考 split/consistency_process/consistency_sql_reader.py)

    Returns:
        list: 查询结果列表，每个元素是元组
    """
    connection = MySQLClient.get_connection(cfg.db_config)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = list(cursor.fetchall())
    cursor.close()
    connection.close()
    return result


def exec_sql_by_pymysql(sql_text):
    """执行增删改SQL"""
    connection = MySQLClient.get_connection(cfg.db_config)
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


def exec_sql_by_pymysql_with_rowcount(sql_text):
    """执行增删改SQL并返回影响行数"""
    update_flag = 0
    connection = MySQLClient.get_connection(cfg.db_config)
    cursor = connection.cursor()
    cursor.execute(sql_text)

    if cursor.rowcount > 0:
        update_flag = 1

    connection.commit()
    cursor.close()
    connection.close()
    return update_flag
