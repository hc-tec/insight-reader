"""
文本处理工具

处理长文本、文本压缩、分块等功能
"""
import re
from typing import List, Optional


class TextProcessor:
    """文本处理器"""

    # 不同分析类型的最大token限制（估算，1 token ≈ 1.5 字符）
    MAX_TOKENS = {
        'unified_analysis': 8000,      # 统一分析：约12000字符
        'meta_analysis': 12000,        # 元分析：约18000字符
        'thinking_lens': 8000,         # 思维透镜：约12000字符
        'spark_analysis': 16000,       # 火花分析：约24000字符
    }

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        估算文本的token数量

        Args:
            text: 输入文本

        Returns:
            估算的token数量
        """
        # 简单估算：中文 1字≈1.5token，英文 1词≈1.3token
        # 这里简化为：总字符数 / 1.5
        return int(len(text) / 1.5)

    @staticmethod
    def truncate_text(text: str, max_tokens: int, strategy: str = 'smart') -> str:
        """
        智能截断文本

        Args:
            text: 原始文本
            max_tokens: 最大token数
            strategy: 截断策略 ('smart', 'head', 'tail', 'middle')

        Returns:
            截断后的文本
        """
        current_tokens = TextProcessor.estimate_tokens(text)

        if current_tokens <= max_tokens:
            return text

        # 计算目标字符数（留10%余量）
        target_chars = int(max_tokens * 1.5 * 0.9)

        if strategy == 'head':
            # 保留开头
            return text[:target_chars] + "\n\n[... 内容过长，已截断 ...]"

        elif strategy == 'tail':
            # 保留结尾
            return "[... 内容过长，已截断 ...]\n\n" + text[-target_chars:]

        elif strategy == 'middle':
            # 保留开头和结尾
            head_chars = target_chars // 2
            tail_chars = target_chars - head_chars
            return text[:head_chars] + "\n\n[... 中间内容已省略 ...]\n\n" + text[-tail_chars:]

        else:  # 'smart'
            # 智能截断：保留开头更多，结尾适量
            # 开头70%，结尾30%
            head_chars = int(target_chars * 0.7)
            tail_chars = int(target_chars * 0.3)
            return text[:head_chars] + "\n\n[... 文章较长，已智能压缩 ...]\n\n" + text[-tail_chars:]

    @staticmethod
    def extract_key_content(text: str, max_tokens: int) -> str:
        """
        提取文本的关键内容

        策略：
        1. 保留所有标题
        2. 保留每段的关键句
        3. 移除重复内容

        Args:
            text: 原始文本
            max_tokens: 最大token数

        Returns:
            提取后的关键内容
        """
        current_tokens = TextProcessor.estimate_tokens(text)

        if current_tokens <= max_tokens:
            return text

        # 分段
        paragraphs = text.split('\n\n')

        # 提取关键内容
        key_parts = []
        total_chars = 0
        target_chars = int(max_tokens * 1.5 * 0.9)

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 检查是否是标题（短且可能有特殊格式）
            is_title = (len(para) < 50 and
                       (para.startswith('#') or
                        para.isupper() or
                        re.match(r'^[一二三四五六七八九十\d]+[、．.]', para)))

            if is_title:
                # 保留所有标题
                key_parts.append(para)
                total_chars += len(para)
            else:
                # 提取段落的关键句（第一句）
                sentences = re.split(r'[。！？\n]', para)
                if sentences:
                    first_sentence = sentences[0].strip()
                    if first_sentence and total_chars + len(first_sentence) < target_chars:
                        key_parts.append(first_sentence)
                        total_chars += len(first_sentence)

            if total_chars >= target_chars:
                break

        result = '\n\n'.join(key_parts)

        # 如果提取后仍然太长，使用智能截断
        if TextProcessor.estimate_tokens(result) > max_tokens:
            result = TextProcessor.truncate_text(result, max_tokens, 'smart')

        return result

    @staticmethod
    def split_into_chunks(text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
        """
        将长文本分块

        Args:
            text: 原始文本
            chunk_size: 每块的目标token数
            overlap: 块之间的重叠token数

        Returns:
            文本块列表
        """
        # 转换为字符数
        chunk_chars = int(chunk_size * 1.5)
        overlap_chars = int(overlap * 1.5)

        if len(text) <= chunk_chars:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_chars

            # 尝试在句子边界处分割
            if end < len(text):
                # 向后查找句子结束标记
                for i in range(end, min(end + 100, len(text))):
                    if text[i] in '。！？\n':
                        end = i + 1
                        break

            chunk = text[start:end]
            chunks.append(chunk)

            # 下一块的起始位置（考虑重叠）
            start = end - overlap_chars

            if start >= len(text):
                break

        return chunks

    @staticmethod
    def compress_for_analysis(text: str, analysis_type: str) -> str:
        """
        根据分析类型压缩文本

        Args:
            text: 原始文本
            analysis_type: 分析类型

        Returns:
            压缩后的文本
        """
        max_tokens = TextProcessor.MAX_TOKENS.get(analysis_type, 8000)
        current_tokens = TextProcessor.estimate_tokens(text)

        if current_tokens <= max_tokens:
            return text

        # 根据超出程度选择策略
        overflow_ratio = current_tokens / max_tokens

        if overflow_ratio < 1.5:
            # 轻微超出：智能截断
            return TextProcessor.truncate_text(text, max_tokens, 'smart')
        elif overflow_ratio < 2.5:
            # 中度超出：提取关键内容
            return TextProcessor.extract_key_content(text, max_tokens)
        else:
            # 严重超出：激进截断（保留开头为主）
            return TextProcessor.truncate_text(text, max_tokens, 'head')


def smart_truncate(text: str, max_length: int = 12000) -> str:
    """
    智能截断文本的便捷函数

    Args:
        text: 原始文本
        max_length: 最大字符数

    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text

    processor = TextProcessor()
    max_tokens = int(max_length / 1.5)
    return processor.truncate_text(text, max_tokens, 'smart')
