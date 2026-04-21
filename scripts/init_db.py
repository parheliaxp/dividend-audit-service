"""
数据库初始化脚本
"""

import sys
sys.path.append('.')

from app.logger import logger
from modules.common.db_client import exec_sql

# 创建审核结果表
CREATE_RESULT_TABLE = """
CREATE TABLE IF NOT EXISTS dividend_audit_result (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    doc_id BIGINT NOT NULL COMMENT '文档ID',
    status INT DEFAULT 0 COMMENT '审核状态: 0=无问题, 1=有问题',
    audit_result TEXT COMMENT '审核结果JSON',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    env VARCHAR(50) COMMENT '环境标识',
    INDEX idx_doc_id (doc_id),
    INDEX idx_create_time (create_time),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分红数据审核结果表'
"""

# 创建审核日志表
CREATE_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS dividend_audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    doc_id BIGINT NOT NULL COMMENT '文档ID',
    action VARCHAR(50) COMMENT '操作类型',
    message TEXT COMMENT '日志信息',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_doc_id (doc_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分红数据审核日志表'
"""

def init_database():
    """初始化数据库表"""
    tables = [
        ('dividend_audit_result', CREATE_RESULT_TABLE),
        ('dividend_audit_log', CREATE_LOG_TABLE)
    ]

    for table_name, create_sql in tables:
        try:
            exec_sql(create_sql)
            logger.info("表 {} 创建成功".format(table_name))
        except Exception as e:
            logger.error("表 {} 创建失败: {}".format(table_name, e))

    logger.info("数据库初始化完成")

if __name__ == '__main__':
    init_database()
