"""
分红审核处理器测试
"""

import sys
sys.path.append('..')

import unittest
from modules.dividend_audit.processor import DividendProcessor
from modules.dividend_audit.text_condenser import TextCondenser

class TestTextCondenser(unittest.TestCase):
    """文本浓缩器测试"""

    def setUp(self):
        self.condenser = TextCondenser(max_length=1000)

    def test_condense_with_dividend_keywords(self):
        """测试包含分红关键词的文本"""
        paragraphs = [
            {'text': '本公司2024年度分红方案如下：每股派发现金红利0.5元。', 'style': None},
            {'text': '这是一段无关内容。', 'style': None}
        ]

        result = self.condenser.condense(paragraphs)

        self.assertIn('分红', result)
        self.assertNotIn('无关内容', result)

    def test_condense_with_financial_data(self):
        """测试包含财务数据的文本"""
        paragraphs = [
            {'text': '净利润达到1.5亿元，同比增长20%。', 'style': None}
        ]

        result = self.condenser.condense(paragraphs)

        self.assertIn('1.5亿元', result)

    def test_condense_empty_paragraphs(self):
        """测试空段落列表"""
        result = self.condenser.condense([])
        self.assertEqual(result, '')

class TestDividendProcessor(unittest.TestCase):
    """分红审核处理器测试"""

    def test_error_result(self):
        """测试错误结果生成"""
        processor = DividendProcessor()
        result = processor._error_result("测试错误", doc_id=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], '系统错误')
        self.assertIn('测试错误', result[0]['content'])

if __name__ == '__main__':
    unittest.main()
