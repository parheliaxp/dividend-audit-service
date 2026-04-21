# 分红数据审核接口文档

## 接口地址

| 配置项 | 值 |
|--------|-----|
| **Path** | `/jzai/doc-audit/dividend_audit` |
| **Method** | `POST` / `GET` |
| **Content-Type** | `application/json` |

---

## 请求参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| doc_id | int | ✅ | - | 文档ID |
| audit_type | int | ❌ | 1 | 审核类型 |
| encrypt_flag | bool | ❌ | true | 文档是否加密存储 |
| callback_url | string | ❌ | - | 回调通知URL |

### 请求示例

```json
POST /jzai/doc-audit/dividend_audit
Content-Type: application/json

{
    "doc_id": 101,
    "audit_type": 1,
    "encrypt_flag": true,
    "callback_url": "http://your-service/callback"
}
```

---

## 返回参数

### 成功响应

```json
{
    "status": 200,
    "message": "ok",
    "result": [
        {
            "type": "数据不一致",
            "content": "分红总额计算有误",
            "reason": "分红总额应为1500万元，文档中为1000万元",
            "suggestion": "请核实分红总额或每股分红数据",
            "l1_type": "是否存在数据计算错误或前后矛盾",
            "l2_type": "分红数据审核"
        }
    ]
}
```

### 失败响应

```json
{
    "status": 500,
    "message": "失败: 错误描述",
    "result": []
}
```

### result 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 错误类型 |
| content | string | 问题内容描述 |
| reason | string | 错误原因说明 |
| suggestion | string | 修正建议 |
| l1_type | string | 一级分类 |
| l2_type | string | 二级分类 |

---

## 健康检查接口

```
GET /health
```

返回:

```json
{
    "status": "ok",
    "service": "dividend-audit-service",
    "version": "1.0.0",
    "env": "dev"
}
```
