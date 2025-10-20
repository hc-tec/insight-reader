# -*- coding: utf-8 -*-
"""
句子拆分工具

使用 stanza NLP 库进行高质量的中文分句
"""

import re
from typing import List, Dict
import stanza
from functools import lru_cache

# 全局 stanza pipeline
_nlp_pipeline = None


def _get_nlp_pipeline():
    """获取或初始化 stanza pipeline（单例模式）"""
    global _nlp_pipeline
    if _nlp_pipeline is None:
        print("🔧 正在初始化 Stanza 中文分句模型...")
        try:
            # 尝试加载中文模型
            _nlp_pipeline = stanza.Pipeline(
                lang='zh',
                processors='tokenize',  # 只使用分句功能，速度更快
                tokenize_no_ssplit=False,  # 启用句子拆分
                use_gpu=False,  # 根据你的环境可以设置为 True
                download_method=None  # 不自动下载，假设已安装
            )
            print("✅ Stanza 中文分句模型加载成功")
        except Exception as e:
            print(f"⚠️ Stanza 模型加载失败: {e}")
            print("💡 请运行: python -m stanza.download('zh')")
            raise RuntimeError(
                "Stanza 中文模型未安装。请运行: python -m stanza.download('zh')"
            ) from e
    return _nlp_pipeline


class SentenceSplitter:
    """句子拆分器 - 使用 Stanza NLP 进行高质量中文分句"""

    @staticmethod
    def split_into_sentences(text: str, use_stanza: bool = True) -> List[str]:
        """
        将文本拆分为句子列表

        Args:
            text: 纯文本（不包含 HTML 标签）
            use_stanza: 是否使用 stanza NLP（默认 True）
                       False 则使用简单正则表达式（更快但精度低）

        Returns:
            句子数组
        """
        if not text or not text.strip():
            return []

        # 预处理：统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        if use_stanza:
            return SentenceSplitter._split_with_stanza(text)
        else:
            return SentenceSplitter._split_with_regex(text)

    @staticmethod
    def _split_with_stanza(text: str) -> List[str]:
        """
        使用 Stanza NLP 进行分句（推荐）

        优点：
        - 准确识别中文句子边界
        - 正确处理引号、括号内的句子
        - 处理省略号、感叹号、问号的复杂组合
        - 避免误拆分（如人名中的点、缩写等）
        """
        try:
            nlp = _get_nlp_pipeline()
            doc = nlp(text)

            sentences = []
            for sentence in doc.sentences:
                sentence_text = sentence.text.strip()
                if sentence_text:
                    sentences.append(sentence_text)

            return sentences

        except Exception as e:
            print(f"⚠️ Stanza 分句失败，回退到正则表达式方法: {e}")
            return SentenceSplitter._split_with_regex(text)

    @staticmethod
    def _split_with_regex(text: str) -> List[str]:
        """
        使用正则表达式进行分句（快速但精度较低）

        规则：
        - 中文：按 。！？…\n 拆分
        - 英文：按 .!?\n 拆分，处理常见缩写
        - 保留标点符号
        - 过滤空句子
        """
        # 常见英文缩写
        ABBREVIATIONS = [
            'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sr.', 'Jr.',
            'etc.', 'vs.', 'e.g.', 'i.e.', 'U.S.', 'U.K.',
            'Inc.', 'Ltd.', 'Co.', 'Corp.'
        ]

        # 句子分隔符（中文和英文）
        sentence_delimiter_pattern = r'([。！？!?.…]+[\s\n]|[\n])'

        # 拆分并保留分隔符
        parts = re.split(sentence_delimiter_pattern, text)

        sentences = []
        current_sentence = ''

        for i in range(len(parts)):
            part = parts[i]

            if not part:
                continue

            # 如果是分隔符
            if re.match(sentence_delimiter_pattern, part):
                current_sentence += part

                # 检查是否是真正的句子结束（排除缩写等）
                next_part = parts[i + 1] if i + 1 < len(parts) else None
                if _is_valid_sentence_end(current_sentence, next_part, ABBREVIATIONS):
                    trimmed = current_sentence.strip()
                    if trimmed:
                        sentences.append(trimmed)
                        current_sentence = ''
            else:
                current_sentence += part

        # 处理最后一个句子
        trimmed = current_sentence.strip()
        if trimmed:
            sentences.append(trimmed)

        return [s for s in sentences if s]

    @staticmethod
    def split_into_paragraphs(text: str, use_stanza: bool = True) -> List[Dict]:
        """
        将纯文本拆分为段落和句子

        Args:
            text: 纯文本
            use_stanza: 是否使用 stanza NLP（默认 True）

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
            sentence_texts = SentenceSplitter.split_into_sentences(
                paragraph_text,
                use_stanza=use_stanza
            )

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


def _is_valid_sentence_end(sentence: str, next_part: str = None, abbreviations: List[str] = None) -> bool:
    """
    判断是否为有效的句子结束

    排除常见缩写：
    - Mr. Mrs. Dr. Prof. etc.
    - U.S. U.K. etc.
    """
    if abbreviations is None:
        abbreviations = []

    # 如果句子以换行结束，一定是句子结束
    if sentence.endswith('\n'):
        return True

    # 检查是否以缩写结尾
    for abbr in abbreviations:
        if sentence.strip().endswith(abbr):
            # 如果下一个部分以小写字母开头，说明不是句子结束
            if next_part and re.match(r'^[a-z]', next_part.strip()):
                return False

    return True


# 便捷函数
def split_sentences(text: str, use_stanza: bool = True) -> List[str]:
    """
    拆分句子

    Args:
        text: 输入文本
        use_stanza: 是否使用 stanza NLP（默认 True，推荐）

    Returns:
        句子列表
    """
    return SentenceSplitter.split_into_sentences(text, use_stanza=use_stanza)


def split_paragraphs(text: str, use_stanza: bool = True) -> List[Dict]:
    """
    拆分段落和句子

    Args:
        text: 输入文本
        use_stanza: 是否使用 stanza NLP（默认 True，推荐）

    Returns:
        段落和句子的结构化数据
    """
    return SentenceSplitter.split_into_paragraphs(text, use_stanza=use_stanza)
