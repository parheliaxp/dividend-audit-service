"""
文本浓缩器测试
"""

import sys
sys.path.append('..')

import unittest
from modules.dividend_audit.text_condenser import TextCondenser

class TestTextCondenser(unittest.TestCase):
    """文本浓缩器测试类"""

    def setUp(self):
        self.condenser = TextCondenser(max_length=500)

    def test_filter_relevant_dividend_keywords(self):
        """测试分红关键词筛选"""
        paragraphs = [
            {'text': '2024年分红方案公布', 'style': None},
            {'text': '每股股利0.3元', 'style': None},
            {'text': '这是一段普通文本', 'style': None}
        ]

        result = self.condenser._filter_relevant(paragraphs)

        self.assertEqual(len(result), 2)

    def test_filter_relevant_financial_data(self):
        """测试财务数据筛选"""
        paragraphs = [
            {'text': '净利润1.5亿元', 'style': None},
            {'text': '每股收益0.5元', 'style': None},
            {'text': '普通文本无数据', 'style': None}
        ]

        result = self.condenser._filter_relevant(paragraphs)

        self.assertGreaterEqual(len(result), 2)

    def test_clean_content(self):
        """测试内容清洗"""
        paragraphs = [
            {'text': '本报告仅供参考，不构成投资建议', 'style': None},
            {'text': '投资者应注意风险', 'style': None},
            {'text': '正常内容保留', 'style': None}
        ]

        result = self.condenser._clean_content(paragraphs)

        # 检查排除模式是否生效
        for text in result:
            self.assertNotIn('仅供参考', text)

    def test_merge_and_truncate(self):
        """测试合并和截断"""
        paragraphs = ['段落1', '段落2', '段落3']

        result = self.condenser._merge_and_truncate(paragraphs)

        self.assertIn('段落1', result)
        self.assertIn('段落2', result)
        self.assertIn('段落3', result)

    def test_max_length_truncation(self):
        """测试最大长度截断"""
        long_paragraphs = ['很长的内容' * 100]

        result = self.condenser._merge_and_truncate(long_paragraphs)

        self.assertLessEqual(len(result), 500)

if __name__ == '__main__':
    unittest.main()
