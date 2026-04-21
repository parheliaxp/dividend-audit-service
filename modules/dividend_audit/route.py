from flask import jsonify, request
from app.logger import logger
import traceback
from .processor import DividendProcessor

def request_parse(req_data):
    """解析请求参数"""
    if req_data.method == 'POST':
        try:
            args = req_data.json
        except:
            args = req_data.form
    else:
        args = req_data.args
    return dict(args) if args else {}

def dividend_audit():
    """
    分红数据审核接口

    请求参数:
    {
        "doc_id": 101,           # 必填，文档ID
        "audit_type": 1,         # 可选，审核类型，默认1
        "encrypt_flag": true,    # 可选，是否加密，默认true
        "callback_url": "http://xxx/callback"  # 可选，回调URL
    }

    返回参数:
    {
        "status": 200,
        "message": "ok",
        "result": [
            {
                "type": "数据不一致",
                "content": "问题描述",
                "reason": "原因说明",
                "suggestion": "修正建议",
                "l1_type": "分类",
                "l2_type": "分红数据审核"
            }
        ]
    }
    """
    try:
        args = request_parse(request)
        logger.info("dividend_audit 请求: {}".format(args))

        # 参数校验
        doc_id = args.get("doc_id")
        if not doc_id:
            result = {
                "status": 400,
                "message": "缺少必填参数: doc_id"
            }
            return jsonify(result)

        # 执行审核
        processor = DividendProcessor()
        audit_result = processor.process(args)

        result = {
            "status": 200,
            "message": "ok",
            "result": audit_result
        }

        logger.info("dividend_audit 完成, doc_id: {}, 问题数: {}".format(doc_id, len(audit_result)))
        return jsonify(result)

    except Exception as e:
        logger.error("dividend_audit 错误: {}".format(e))
        logger.error(traceback.format_exc())

        result = {
            "status": 500,
            "message": "失败: {}".format(str(e)),
            "result": []
        }
        return jsonify(result)
