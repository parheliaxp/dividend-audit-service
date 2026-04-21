# 部署文档

## 本地开发环境

### 1. 安装依赖

```bash
cd dividend-audit-service
pip install -r requirements.txt
```

### 2. 配置环境

```bash
export ENV=dev
# 或创建 .env 文件
cp .env.example .env
```

### 3. 启动服务

```bash
python app/main.py
```

---

## Docker 部署

### 1. 构建镜像

```bash
docker build -f docker/Dockerfile -t dividend-audit-service:1.0.0 .
```

### 2. 运行容器

```bash
docker run -d \
    --name dividend-audit \
    -p 6768:6768 \
    -e ENV=dev \
    dividend-audit-service:1.0.0
```

---

## Kubernetes 部署

### 1. 创建命名空间 (可选)

```bash
kubectl create namespace dividend-audit
```

### 2. 创建密钥

```bash
kubectl apply -f k8s/secret.yaml
```

### 3. 创建配置

```bash
kubectl apply -f k8s/configmap.yaml
```

### 4. 部署服务

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 5. 创建入口 (可选)

```bash
kubectl apply -f k8s/ingress.yaml
```

### 6. 检查状态

```bash
kubectl get pods -l app=dividend-audit
kubectl logs -f deployment/dividend-audit-service
```

---

## 数据库初始化

```bash
python scripts/init_db.py
```

---

## 健康检查

```bash
curl http://localhost:6768/health
```
