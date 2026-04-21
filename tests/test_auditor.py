"""
LLM审核器测试
"""

import sys
sys.path.append('..')

import unittest
from modules.dividend_audit.llm_auditor import DividendAuditor

class TestDividendAuditor(unittest.TestCase):
    """LLM审核器测试类"""

    def setUp(self):
        self.auditor = DividendAuditor(max_retries=1)

    def test_parse_json_response_direct(self):
        """测试直接JSON解析"""
        response = '{"key": "value"}'

        result = self.auditor._parse_json_response(response)

        self.assertEqual(result['key'], 'value')

    def test_parse_json_response_code_block(self):
        """测试代码块JSON解析"""
        response = '''
        ```json
        {"key": "value"}
        ```
        '''

        result = self.auditor._parse_json_response(response)

        self.assertEqual(result['key'], 'value')

    def test_format_result_list(self):
        """测试列表结果格式化"""
        result = [
            {
                '错误类型': '数据不一致',
                '问题内容': '测试问题',
                '错误原因': '测试原因',
                '修正建议': '测试建议'
            }
        ]

        formatted = self.auditor._format_result(result)

        self.assertEqual(len(formatted), 1)
        self.assertEqual(formatted[0]['type'], '数据不一致')
        self.assertEqual(formatted[0]['l2_type'], '分红数据审核')

    def test_format_result_dict_with_errors(self):
        """测试字典结果格式化(有错误)"""
        result = {
            '是否一致': '否',
            '错误列表': [
                {
                    '错误类型': '计算错误',
                    '问题内容': '计算有误',
                    '错误原因': '原因说明',
                    '修正建议': '修正建议'
                }
            ]
        }

        formatted = self.auditor._format_result(result)

        self.assertEqual(len(formatted), 1)

    def test_format_result_dict_no_errors(self):
        """测试字典结果格式化(无错误)"""
        result = {
            '是否一致': '是',
            '错误列表': []
        }

        formatted = self.auditor._format_result(result)

        self.assertEqual(len(formatted), 0)

if __name__ == '__main__':
    unittest.main()
