import pymysql
import pandas as pd
from app.logger import logger
from app.config import cfg

class DBClient:
    """数据库客户端"""

    def __init__(self):
        self.config = cfg.DbConfig
        self.connection = None

    def get_connection(self):
        """获取数据库连接"""
        if self.connection is None or not self.connection.open:
            self.connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4',
                connect_timeout=10
            )
        return self.connection

    def execute_query(self, sql):
        """
        执行查询

        Args:
            sql: SQL查询语句

        Returns:
            DataFrame: 查询结果
        """
        conn = self.get_connection()
        return pd.read_sql(sql, conn)

    def execute_sql(self, sql):
        """
        执行SQL语句

        Args:
            sql: SQL语句

        Returns:
            bool: 执行是否成功
        """
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql)
            conn.commit()
        return True

    def close(self):
        """关闭连接"""
        if self.connection and self.connection.open:
            self.connection.close()

# 全局实例
db_client = DBClient()

# 便捷函数
def exec_query_df(sql):
    """执行查询返回DataFrame"""
    return db_client.execute_query(sql)

def exec_sql(sql):
    """执行SQL语句"""
    return db_client.execute_sql(sql)
