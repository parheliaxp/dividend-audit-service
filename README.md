# 分红数据审核服务

## 项目简介

分红数据审核服务是一个独立的微服务，用于对金融文档中的分红数据进行智能审核，检测数据一致性、计算准确性等问题。

## 功能特性

- 📄 **文档解析**: 支持 DOCX 格式文档解析
- 🔍 **文本浓缩**: 智能提取分红相关内容
- 🤖 **LLM审核**: 使用大语言模型进行数据审核
- 💾 **结果入库**: 审核结果持久化存储
- 🔔 **回调通知**: 支持审核完成回调通知
- 🐳 **容器化部署**: 支持 Docker/Kubernetes 部署

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python app/main.py
```

### 测试接口

```bash
curl -X POST http://localhost:6768/jzai/doc-audit/dividend_audit \
    -H "Content-Type: application/json" \
    -d '{"doc_id": 101}'
```

## 项目结构

```
dividend-audit-service/
├── app/                    # 应用入口
├── modules/                # 业务模块
│   ├── dividend_audit/     # 分红审核模块
│   └── common/             # 公共模块
├── config/                 # 配置文件
├── docker/                 # Docker配置
├── k8s/                    # Kubernetes配置
├── tests/                  # 测试文件
└── docs/                   # 文档
```

## API 文档

详见 [docs/api.md](docs/api.md)

## 部署文档

详见 [docs/deployment.md](docs/deployment.md)

## 配置说明

详见 [docs/config.md](docs/config.md)

## 技术栈

- **Web框架**: Flask
- **配置管理**: OmegaConf
- **LLM**: DeepSeek / 通义千问
- **数据库**: MySQL / Vastbase
- **文档解析**: python-docx
- **加解密**: PyCryptodome

## License

MIT
