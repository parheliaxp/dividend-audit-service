import json
import re
from app.logger import logger
from app.config import cfg
from modules.common.llm_client import LLMClient
from .prompt import DIVIDEND_AUDIT_PROMPT, DIVIDEND_EXTRACT_PROMPT

class DividendAuditor:
    """分红数据 LLM 审核器"""

    def __init__(self, max_retries=None):
        self.max_retries = max_retries or cfg.DividendAuditConfig['max_retries']

    def audit(self, condensed_text, doc_id):
        """
        执行分红数据审核

        Args:
            condensed_text: 浓缩后的文本
            doc_id: 文档ID

        Returns:
            list: 审核结果列表
        """
        # Step 1: 提取分红数据
        dividend_data = self._extract_dividend_data(condensed_text)

        if not dividend_data:
            logger.info("doc_id: {} 未提取到分红数据".format(doc_id))
            return []

        # Step 2: 审核分红数据
        audit_result = self._audit_dividend_data(dividend_data, condensed_text)

        return audit_result

    def _extract_dividend_data(self, text):
        """使用 LLM 提取分红数据"""
        prompt = DIVIDEND_EXTRACT_PROMPT.format(text)

        for attempt in range(self.max_retries):
            try:
                response = LLMClient.qianwen_query(prompt, temperature=0)
                data = self._parse_json_response(response)
                logger.info("成功提取分红数据")
                return data
            except Exception as e:
                logger.warning("提取分红数据失败, 尝试 {}/{}: {}".format(
                    attempt + 1, self.max_retries, e
                ))

        return None

    def _audit_dividend_data(self, dividend_data, original_text):
        """审核分红数据一致性"""
        prompt = DIVIDEND_AUDIT_PROMPT.format(
            json.dumps(dividend_data, ensure_ascii=False, indent=2),
            original_text[:3000]  # 限制长度
        )

        for attempt in range(self.max_retries):
            try:
                response = LLMClient.deepseek_query(prompt, temperature=0)
                result = self._parse_json_response(response)
                return self._format_result(result)
            except Exception as e:
                logger.warning("审核分红数据失败, 尝试 {}/{}: {}".format(
                    attempt + 1, self.max_retries, e
                ))

        return []

    def _parse_json_response(self, response):
        """解析 JSON 响应"""
        # 尝试直接解析
        try:
            return json.loads(response)
        except:
            pass

        # 尝试提取 ```json ``` 块
        pattern = r'```json\s*(.*?)\s*```'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass

        # 尝试提取 {} 块
        pattern = r'\{.*\}'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass

        raise ValueError("无法解析 JSON 响应")

    def _format_result(self, result):
        """格式化审核结果"""
        formatted = []

        if isinstance(result, list):
            for item in result:
                formatted.append({
                    'type': item.get('错误类型', '分红数据错误'),
                    'content': item.get('问题内容', ''),
                    'reason': item.get('错误原因', ''),
                    'suggestion': item.get('修正建议', ''),
                    'l1_type': '是否存在数据计算错误或前后矛盾',
                    'l2_type': '分红数据审核'
                })

        elif isinstance(result, dict):
            # 检查是否有错误列表
            if '错误列表' in result and result['错误列表']:
                for item in result['错误列表']:
                    formatted.append({
                        'type': item.get('错误类型', '分红数据错误'),
                        'content': item.get('问题内容', ''),
                        'reason': item.get('错误原因', ''),
                        'suggestion': item.get('修正建议', ''),
                        'l1_type': '是否存在数据计算错误或前后矛盾',
                        'l2_type': '分红数据审核'
                    })
            # 检查是否一致
            elif result.get('是否一致') == '否':
                formatted.append({
                    'type': result.get('错误类型', '分红数据错误'),
                    'content': result.get('问题内容', ''),
                    'reason': result.get('错误原因', ''),
                    'suggestion': result.get('修正建议', ''),
                    'l1_type': '是否存在数据计算错误或前后矛盾',
                    'l2_type': '分红数据审核'
                })

        return formatted
