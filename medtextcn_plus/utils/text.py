"""工具函数：中文文本处理"""

import re
import unicodedata
from typing import List, Tuple


def is_chinese_char(char: str) -> bool:
    """判断是否为中文字符"""
    cp = ord(char)
    if (0x4E00 <= cp <= 0x9FFF or
        0x3400 <= cp <= 0x4DBF or
        0x20000 <= cp <= 0x2A6DF or
        0x2A700 <= cp <= 0x2B73F or
        0x2B740 <= cp <= 0x2B81F or
        0x2B820 <= cp <= 0x2CEAF or
        0xF900 <= cp <= 0xFAFF or
        0x2F800 <= cp <= 0x2FA1F):
        return True
    return False


def contains_chinese(text: str) -> bool:
    """判断文本是否包含中文"""
    return any(is_chinese_char(c) for c in text)


def normalize_text(text: str) -> str:
    """文本规范化：全角转半角、统一空白、去除控制字符"""
    # 全角转半角
    result = []
    for char in text:
        code = ord(char)
        if code == 0x3000:
            code = 0x0020
        elif 0xFF01 <= code <= 0xFF5E:
            code -= 0xFEE0
        result.append(chr(code))
    text = "".join(result)
    # 统一空白
    text = re.sub(r"[\t\r\n]+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    # 去除控制字符
    text = "".join(c for c in text if unicodedata.category(c)[0] != "C" or c in "\n\t")
    return text.strip()


def simple_tokenize(text: str) -> List[str]:
    """简单中文分词：基于规则的贪心最大匹配"""
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        if is_chinese_char(text[i]):
            # 中文字符序列
            j = i
            while j < n and is_chinese_char(text[j]):
                j += 1
            # 对中文序列进行简单切分
            segment = text[i:j]
            tokens.extend(_segment_chinese(segment))
            i = j
        elif text[i].isalnum() or text[i] == "_":
            j = i
            while j < n and (text[j].isalnum() or text[j] == "_"):
                j += 1
            tokens.append(text[i:j])
            i = j
        elif text[i] in " \t\n\r":
            i += 1
        else:
            tokens.append(text[i])
            i += 1
    return tokens


def _segment_chinese(text: str) -> List[str]:
    """简单中文分词：2-4字词优先"""
    if len(text) <= 1:
        return list(text) if text else []
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        # 尝试4字、3字、2字、1字
        matched = False
        for length in [4, 3, 2]:
            if i + length <= n:
                tokens.append(text[i:i + length])
                i += length
                matched = True
                break
        if not matched:
            tokens.append(text[i])
            i += 1
    return tokens


def extract_sentences(text: str) -> List[str]:
    """中文文本断句"""
    # 按中文标点断句
    sentences = re.split(r"[。！？；\n]+", text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_text_similarity(text_a: str, text_b: str) -> float:
    """基于字符重叠的简单文本相似度计算"""
    if not text_a or not text_b:
        return 0.0
    set_a = set(text_a)
    set_b = set(text_b)
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def count_chinese_chars(text: str) -> int:
    """统计中文字符数"""
    return sum(1 for c in text if is_chinese_char(c))


def detect_text_language(text: str) -> str:
    """检测文本主要语言"""
    chinese_count = count_chinese_chars(text)
    total_alpha = sum(1 for c in text if c.isalpha())
    if total_alpha == 0:
        return "unknown"
    ratio = chinese_count / total_alpha
    if ratio > 0.3:
        return "zh"
    return "en"
