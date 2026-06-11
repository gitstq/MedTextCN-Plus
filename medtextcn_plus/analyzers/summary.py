"""文本摘要分析器 — 抽取式中文医疗文本摘要"""

import re
import math
from typing import List, Dict, Tuple
from collections import Counter

from medtextcn_plus.utils.text import extract_sentences, simple_tokenize, normalize_text


class TextSummarizer:
    """抽取式中文文本摘要器"""

    def __init__(self):
        """初始化摘要器"""
        self._stop_words = self._build_stop_words()

    def summarize(
        self,
        text: str,
        max_length: int = 100,
        sentence_count: int = 3,
        method: str = "frequency"
    ) -> str:
        """
        生成文本摘要

        Args:
            text: 输入文本
            max_length: 摘要最大长度
            sentence_count: 摘要最大句数
            method: 摘要方法 (frequency, position, combined)

        Returns:
            摘要文本
        """
        sentences = extract_sentences(text)
        if len(sentences) <= sentence_count:
            return text[:max_length]

        if method == "frequency":
            scores = self._frequency_score(sentences)
        elif method == "position":
            scores = self._position_score(sentences)
        else:
            freq_scores = self._frequency_score(sentences)
            pos_scores = self._position_score(sentences)
            scores = {
                i: 0.6 * freq_scores.get(i, 0) + 0.4 * pos_scores.get(i, 0)
                for i in range(len(sentences))
            }

        # 按分数排序选取句子
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        selected_indices = sorted([idx for idx, _ in ranked[:sentence_count]])

        summary = "".join(sentences[i] for i in selected_indices)
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        return summary

    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """提取关键词"""
        tokens = simple_tokenize(normalize_text(text))
        # 过滤停用词和短词
        filtered = [t for t in tokens if t not in self._stop_words and len(t) >= 2]
        freq = Counter(filtered)
        total = sum(freq.values()) if freq.values() else 1
        keywords = [(word, count / total) for word, count in freq.most_common(top_n)]
        return keywords

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """简单情感分析"""
        positive_words = [
            "好转", "改善", "恢复", "正常", "稳定", "缓解", "治愈",
            "有效", "良好", "健康", "成功", "进步", "满意", "康复",
        ]
        negative_words = [
            "恶化", "加重", "异常", "疼痛", "严重", "危险", "失败",
            "无效", "不良", "并发症", "复发", "死亡", "恶化", "恶化",
            "感染", "出血", "梗阻", "破裂",
        ]

        tokens = simple_tokenize(normalize_text(text))
        pos_count = sum(1 for t in tokens if t in positive_words)
        neg_count = sum(1 for t in tokens if t in negative_words)
        total = pos_count + neg_count

        if total == 0:
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0, "overall": 0.0}

        return {
            "positive": pos_count / total,
            "negative": neg_count / total,
            "neutral": 0.0,
            "overall": (pos_count - neg_count) / total,
        }

    def classify_text(self, text: str) -> Dict[str, float]:
        """文本分类"""
        categories = {
            "门诊": ["门诊", "就诊", "挂号", "预约", "候诊"],
            "住院": ["住院", "入院", "出院", "病房", "床位", "医嘱"],
            "检查": ["检查", "检验", "化验", "影像", "超声", "CT", "MRI"],
            "手术": ["手术", "术前", "术后", "麻醉", "切口", "缝合"],
            "用药": ["处方", "用药", "服药", "注射", "输液", "药物"],
            "护理": ["护理", "换药", "翻身", "吸痰", "导尿"],
            "随访": ["随访", "复查", "复诊", "回访"],
        }

        tokens = simple_tokenize(normalize_text(text))
        scores = {}
        for category, keywords in categories.items():
            match_count = sum(1 for t in tokens if t in keywords)
            scores[category] = match_count / max(1, len(tokens))

        return scores

    def _frequency_score(self, sentences: List[str]) -> Dict[int, float]:
        """基于词频的句子评分"""
        # 计算全文词频
        all_tokens = []
        sentence_tokens = []
        for sent in sentences:
            tokens = simple_tokenize(normalize_text(sent))
            sentence_tokens.append(tokens)
            all_tokens.extend(tokens)

        if not all_tokens:
            return {i: 0.0 for i in range(len(sentences))}

        doc_freq = Counter(all_tokens)
        max_freq = max(doc_freq.values())

        scores = {}
        for i, tokens in enumerate(sentence_tokens):
            if not tokens:
                scores[i] = 0.0
                continue
            score = sum(doc_freq.get(t, 0) / max_freq for t in tokens) / len(tokens)
            scores[i] = score
        return scores

    def _position_score(self, sentences: List[str]) -> Dict[int, float]:
        """基于位置的句子评分"""
        n = len(sentences)
        scores = {}
        for i in range(n):
            # 首句和尾句权重更高
            if i == 0:
                scores[i] = 1.0
            elif i == n - 1:
                scores[i] = 0.8
            else:
                scores[i] = max(0.1, 1.0 - (i / n) * 0.5)
        return scores

    def _build_stop_words(self) -> set:
        """构建中文停用词表"""
        return {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
            "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
            "你", "会", "着", "没有", "看", "好", "自己", "这", "他", "她",
            "它", "们", "那", "被", "从", "把", "让", "用", "对", "与",
            "为", "以", "及", "等", "但", "而", "或", "如", "因", "所",
            "其", "此", "中", "将", "可", "能", "已", "还", "又", "才",
            "比", "更", "最", "并", "且", "则", "若", "虽", "每", "各",
            "该", "之", "于", "至", "当", "后", "前", "间", "内", "外",
            "时", "日", "月", "年", "号", "例", "次", "型", "级", "种",
            "个", "位", "名", "岁", "男", "女", "患者", "入院", "出院",
            "因", "于", "予", "给", "行", "做", "查", "示", "见", "无",
            "有", "未", "已", "正", "在", "为", "以", "其", "所", "此",
        }
