import re
from app.logger import logger
from app.config import cfg

class TextCondenser:
    """文本浓缩器 - 提取分红相关内容"""

    # 分红相关关键词
    DIVIDEND_KEYWORDS = [
        '分红', '股息', '派息', '现金分红', '股票股利',
        '每股收益', '每股股利', '分红比例', '分红方案',
        '利润分配', '股利支付', '分红金额', '分红总额',
        '股权登记日', '除权除息日', '红利', '派发',
        '股利', '现金股利', '股票股利', '转增'
    ]

    # 需要排除的无关内容
    EXCLUDE_PATTERNS = [
        r'本报告.*仅供参考',
        r'投资者.*注意.*风险',
        r'本公司.*承诺',
        r'不构成.*投资建议',
    ]

    def __init__(self, max_length=None):
        self.max_length = max_length or cfg.DividendAuditConfig['max_text_length']

    def condense(self, paragraphs):
        """
        浓缩文本，提取分红相关内容

        Args:
            paragraphs: 段落列表 [{'text': str, 'style': str}, ...]

        Returns:
            str: 浓缩后的文本
        """
        # Step 1: 筛选分红相关段落
        relevant_paragraphs = self._filter_relevant(paragraphs)
        logger.info("筛选出相关段落数: {}".format(len(relevant_paragraphs)))

        # Step 2: 清洗无关内容
        cleaned_paragraphs = self._clean_content(relevant_paragraphs)

        # Step 3: 合并并截断
        condensed_text = self._merge_and_truncate(cleaned_paragraphs)

        return condensed_text

    def _filter_relevant(self, paragraphs):
        """筛选分红相关段落"""
        relevant = []

        for para in paragraphs:
            text = para['text']

            # 检查是否包含分红关键词
            if any(kw in text for kw in self.DIVIDEND_KEYWORDS):
                relevant.append(para)
                continue

            # 检查是否包含数字和金额模式
            if self._contains_financial_data(text):
                relevant.append(para)

        return relevant

    def _contains_financial_data(self, text):
        """检查是否包含财务数据"""
        # 匹配金额模式
        patterns = [
            r'\d+\.?\d*\s*[万亿]?元',
            r'每股\s*\d+\.?\d*\s*元?',
            r'\d+\.?\d*%',
            r'\d{4}年\d{1,2}月\d{1,2}日',
        ]

        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    def _clean_content(self, paragraphs):
        """清洗无关内容"""
        cleaned = []

        for para in paragraphs:
            text = para['text']

            # 移除匹配排除模式的内容
            for pattern in self.EXCLUDE_PATTERNS:
                text = re.sub(pattern, '', text)

            text = text.strip()
            if text and len(text) > 5:  # 过滤过短内容
                cleaned.append(text)

        return cleaned

    def _merge_and_truncate(self, paragraphs):
        """合并段落并截断到最大长度"""
        merged = "\n\n".join(paragraphs)

        if len(merged) > self.max_length:
            merged = merged[:self.max_length]
            logger.warning("文本已截断到 {} 字符".format(self.max_length))

        return merged
