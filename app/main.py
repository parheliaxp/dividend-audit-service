import sys
sys.path.append('.')

from flask import Flask, jsonify
from flask_cors import CORS
from app.logger import logger
from app.config import cfg

# 注册路由
from modules.dividend_audit.route import dividend_audit

def create_app():
    """创建 Flask 应用"""
    flask_app = Flask(__name__)
    CORS(flask_app, resources={r"/*": {"origins": "*"}})

    # 注册路由
    flask_app.add_url_rule(
        '/health',
        'health',
        health_check,
        methods=['GET', 'POST']
    )
    flask_app.add_url_rule(
        '/jzai/doc-audit/dividend_audit',
        'dividend_audit',
        dividend_audit,
        methods=['GET', 'POST']
    )
    # Analysis Java 端实际调用的路由
    flask_app.add_url_rule(
        '/dividend_audit/process',
        'dividend_audit_process',
        dividend_audit,
        methods=['POST']
    )

    return flask_app

def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'service': 'dividend-audit-service',
        'version': '1.0.0',
        'env': cfg.env if hasattr(cfg, 'env') else 'unknown'
    })

if __name__ == '__main__':
    app = create_app()
    port = cfg.ServerConfig['port'] if hasattr(cfg, 'ServerConfig') else 6768
    logger.info("分红审核服务启动, 端口: {}".format(port))
    app.run('0.0.0.0', port)
