FROM python:3.9-slim

LABEL maintainer="dividend-audit-service"
LABEL version="1.0.0"
LABEL description="分红数据审核服务"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV ENV=dev

# 暴露端口
EXPOSE 6768

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6768/health || exit 1

# 启动命令
CMD ["python", "app/main.py"]
