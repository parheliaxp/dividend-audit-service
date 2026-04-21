#!/bin/bash

# 健康检查脚本

SERVICE_URL="http://localhost:6768/health"
TIMEOUT=5

response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT $SERVICE_URL)

if [ "$response" -eq 200 ]; then
    echo "Health check passed: HTTP $response"
    exit 0
else
    echo "Health check failed: HTTP $response"
    exit 1
fi
