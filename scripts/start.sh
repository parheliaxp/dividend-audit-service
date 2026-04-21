#!/bin/bash

# 分红审核服务启动脚本

APP_NAME="dividend-audit-service"
APP_DIR="/app"
LOG_DIR="/app/logs"

# 创建日志目录
mkdir -p $LOG_DIR

# 设置环境变量
export ENV=${ENV:-"dev"}
export PYTHONUNBUFFERED=1

echo "=========================================="
echo "Starting $APP_NAME"
echo "Environment: $ENV"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 启动服务
cd $APP_DIR

if [ "$ENV" = "prd" ]; then
    # 生产环境使用 gunicorn
    gunicorn \
        --bind 0.0.0.0:6768 \
        --workers 4 \
        --timeout 300 \
        --access-logfile $LOG_DIR/access.log \
        --error-logfile $LOG_DIR/error.log \
        --log-level info \
        app.main:app
else
    # 开发环境使用 Flask
    python app/main.py
fi
