# 配置说明文档

## 配置文件结构

```
config/
├── config.yaml      # 基础配置
├── env_dev.yaml     # 开发环境
├── env_qa.yaml      # 测试环境
├── env_uat.yaml     # UAT环境
└── env_prd.yaml     # 生产环境
```

---

## 配置项说明

### ServerConfig - 服务配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| port | int | 6768 | 服务端口 |
| workers | int | 4 | Worker进程数 |
| timeout | int | 300 | 请求超时时间(秒) |

### DbConfig - 数据库配置

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 数据库类型 (mysql/vastbase) |
| host | string | 数据库地址 |
| port | int | 数据库端口 |
| user | string | 用户名 |
| password | string | 密码 |
| database | string | 数据库名 |

### LlmConfig - LLM配置

| 字段 | 类型 | 说明 |
|------|------|------|
| deepseek.url | string | DeepSeek服务地址 |
| deepseek.model | string | 模型名称 |
| deepseek.max_tokens | int | 最大token数 |
| qianwen.url | string | 通义千问服务地址 |

### DividendAuditConfig - 分红审核配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | bool | true | 是否启用 |
| max_text_length | int | 8000 | 最大文本长度 |
| max_retries | int | 3 | 最大重试次数 |
| callback_timeout | int | 30 | 回调超时时间 |

### EncryptionConfig - 加解密配置

| 字段 | 类型 | 说明 |
|------|------|------|
| secret_key | string | AES密钥 (16字节) |
| iv | string | 初始向量 (16字节) |

---

## 环境变量

通过 `ENV` 环境变量指定运行环境:

```bash
export ENV=dev   # 开发环境
export ENV=qa    # 测试环境
export ENV=uat   # UAT环境
export ENV=prd   # 生产环境
```
