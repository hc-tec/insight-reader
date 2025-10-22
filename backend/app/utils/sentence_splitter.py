# -*- coding: utf-8 -*-
"""
句子拆分工具

使用优化的规则方法进行中文分句（轻量级，零依赖）
"""

import re
from typing import List, Dict


class SentenceSplitter:
    """句子拆分器 - 使用规则方法进行高质量中文分句"""

    # 常见英文缩写
    ABBREVIATIONS = [
        'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sr.', 'Jr.',
        'etc.', 'vs.', 'e.g.', 'i.e.', 'U.S.', 'U.K.',
        'Inc.', 'Ltd.', 'Co.', 'Corp.', 'St.', 'Ave.',
        'Ph.D.', 'M.D.', 'B.A.', 'M.A.', 'D.C.'
    ]

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """
        将文本拆分为句子列表

        Args:
            text: 纯文本（不包含 HTML 标签）

        Returns:
            句子数组
        """
        if not text or not text.strip():
            return []

        # 预处理：统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        return SentenceSplitter._split_with_enhanced_rules(text)

    @staticmethod
    def _split_with_enhanced_rules(text: str) -> List[str]:
        """
        使用增强规则进行分句

        规则优化：
        1. 识别中文句子结束标点：。！？；…
        2. 识别英文句子结束标点：.!?;
        3. 处理引号、括号内的句子
        4. 处理省略号、感叹号的组合
        5. 处理英文缩写（避免误拆分）
        6. 处理换行符（强制句子边界）
        7. 处理数字、日期（避免误拆分）
        """
        sentences = []

        # 步骤1: 按段落预处理
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            if not para.strip():
                continue

            # 步骤2: 在段落内进行分句
            para_sentences = SentenceSplitter._split_paragraph(para)
            sentences.extend(para_sentences)

        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def _split_paragraph(text: str) -> List[str]:
        """在段落内进行精细分句"""

        # 句子分隔符的正则模式
        # 匹配：中文标点(。！？；…) + 可选空白
        #      英文标点(.!?;) + 空白
        #      换行符
        pattern = r'([。！？；…]+\s*|[.!?]+\s+|\n)'

        parts = re.split(pattern, text)

        sentences = []
        current = ''
        i = 0

        while i < len(parts):
            part = parts[i]

            if not part:
                i += 1
                continue

            # 如果是分隔符
            if re.match(pattern, part):
                current += part

                # 检查是否应该在此处断句
                next_part = parts[i + 1] if i + 1 < len(parts) else ''

                if SentenceSplitter._should_break(current, next_part):
                    sentences.append(current.strip())
                    current = ''
                # 否则继续累积
            else:
                current += part

            i += 1

        # 添加最后一个句子
        if current.strip():
            sentences.append(current.strip())

        return sentences

    @staticmethod
    def _should_break(current: str, next_part: str) -> bool:
        """
        判断是否应该在当前位置断句

        Args:
            current: 当前累积的文本
            next_part: 下一个文本片段

        Returns:
            是否应该断句
        """
        current = current.strip()

        # 空文本，不断句
        if not current:
            return False

        # 以换行符结束，强制断句
        if current.endswith('\n'):
            return True

        # 检查是否以英文缩写结尾
        for abbr in SentenceSplitter.ABBREVIATIONS:
            if current.endswith(abbr):
                # 如果下一部分以小写字母开头，不断句
                if next_part and re.match(r'^[a-z]', next_part.strip()):
                    return False

        # 检查是否是数字 + 点（如：3.14, 1.5）
        if re.search(r'\d+\.\s*$', current):
            if next_part and re.match(r'^\d', next_part.strip()):
                return False

        # 检查是否在引号或括号内
        # 如果引号、括号未闭合，不断句
        open_quotes = current.count('"') + current.count('"') + current.count('「')
        close_quotes = current.count('"') + current.count('"') + current.count('」')
        open_parens = current.count('(') + current.count('（')
        close_parens = current.count(')') + current.count('）')

        if open_quotes % 2 != 0 or open_quotes != close_quotes:
            return False
        if open_parens != close_parens:
            return False

        # 以中文句子结束标点结尾，断句
        if re.search(r'[。！？；…]$', current):
            return True

        # 以英文句子结束标点 + 空白结尾，断句
        if re.search(r'[.!?]\s+$', current):
            return True

        # 默认不断句
        return False

    @staticmethod
    def split_into_paragraphs(text: str) -> List[Dict]:
        """
        将纯文本拆分为段落和句子

        Args:
            text: 纯文本

        Returns:
            段落数组，每个段落包含句子列表
            [
                {
                    "index": 0,
                    "sentences": [
                        {"index": 0, "text": "...", "paragraph_index": 0},
                        {"index": 1, "text": "...", "paragraph_index": 0}
                    ]
                }
            ]
        """
        # 按双换行拆分段落
        raw_paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]

        paragraphs = []
        global_sentence_index = 0

        for paragraph_index, paragraph_text in enumerate(raw_paragraphs):
            # 拆分该段落的句子
            sentence_texts = SentenceSplitter.split_into_sentences(paragraph_text)

            sentences = []
            for sentence_text in sentence_texts:
                sentences.append({
                    "index": global_sentence_index,
                    "text": sentence_text,
                    "paragraph_index": paragraph_index
                })
                global_sentence_index += 1

            paragraphs.append({
                "index": paragraph_index,
                "sentences": sentences
            })

        return paragraphs


# 便捷函数
def split_sentences(text: str) -> List[str]:
    """
    拆分句子

    Args:
        text: 输入文本

    Returns:
        句子列表
    """
    return SentenceSplitter.split_into_sentences(text)


def split_paragraphs(text: str) -> List[Dict]:
    """
    拆分段落和句子

    Args:
        text: 输入文本

    Returns:
        段落和句子的结构化数据
    """
    return SentenceSplitter.split_into_paragraphs(text)
