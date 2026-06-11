"""核心分析引擎 — 统一入口"""

from typing import List, Dict, Optional, Any

from medtextcn_plus.analyzers.ner import MedicalNER
from medtextcn_plus.analyzers.pii import PIIDetector
from medtextcn_plus.analyzers.summary import TextSummarizer
from medtextcn_plus.analyzers.relation import RelationExtractor
from medtextcn_plus.analyzers.drug import DrugInteractionDetector
from medtextcn_plus.models.entities import Entity, EntityType, Relation, RelationType
from medtextcn_plus.models.pii import PIIMatch, PIIType, SanitizationResult
from medtextcn_plus.models.drug import DrugInteraction, InteractionSeverity


class MedTextAnalyzer:
    """中文医疗文本智能分析引擎 — 统一入口

    提供NER实体识别、PII脱敏、文本摘要、关系抽取、药物交互检测等功能的统一接口。

    使用示例:
        analyzer = MedTextAnalyzer()
        entities = analyzer.extract_entities(text)
        sanitized = analyzer.sanitize_pii(text)
        summary = analyzer.summarize(text)
    """

    def __init__(self):
        """初始化分析引擎"""
        self._ner = MedicalNER()
        self._pii = PIIDetector()
        self._summarizer = TextSummarizer()
        self._relation_extractor = RelationExtractor()
        self._drug_detector = DrugInteractionDetector()

    def extract_entities(self, text: str) -> List[Entity]:
        """
        从文本中提取医疗实体

        Args:
            text: 输入的医疗文本

        Returns:
            医疗实体列表
        """
        return self._ner.extract(text)

    def extract_entities_with_context(
        self, text: str, context_window: int = 10
    ) -> List[Entity]:
        """提取实体并附加上下文"""
        return self._ner.extract_with_context(text, context_window)

    def detect_pii(self, text: str) -> List[PIIMatch]:
        """
        检测文本中的PII信息

        Args:
            text: 输入文本

        Returns:
            PII匹配列表
        """
        return self._pii.detect(text)

    def sanitize_pii(self, text: str) -> str:
        """
        对文本进行PII脱敏

        Args:
            text: 输入文本

        Returns:
            脱敏后的文本
        """
        result = self._pii.sanitize(text)
        return result.sanitized_text

    def sanitize_pii_full(self, text: str) -> SanitizationResult:
        """返回完整的脱敏结果（含匹配详情）"""
        return self._pii.sanitize(text)

    def summarize(
        self,
        text: str,
        max_length: int = 100,
        sentence_count: int = 3,
        method: str = "combined"
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
        return self._summarizer.summarize(
            text, max_length=max_length, sentence_count=sentence_count, method=method
        )

    def extract_keywords(self, text: str, top_n: int = 10) -> list:
        """提取关键词"""
        return self._summarizer.extract_keywords(text, top_n)

    def analyze_sentiment(self, text: str) -> dict:
        """情感分析"""
        return self._summarizer.analyze_sentiment(text)

    def classify_text(self, text: str) -> dict:
        """文本分类"""
        return self._summarizer.classify_text(text)

    def extract_relations(self, text: str) -> List[Relation]:
        """
        抽取医疗实体间的关系

        Args:
            text: 输入文本

        Returns:
            关系列表
        """
        entities = self._ner.extract(text)
        return self._relation_extractor.extract(text, entities)

    def detect_drug_interactions(self, drugs: List[str]) -> List[DrugInteraction]:
        """
        检测药物间的交互作用

        Args:
            drugs: 药物名称列表

        Returns:
            药物交互列表
        """
        return self._drug_detector.detect(drugs)

    def detect_drug_interactions_from_text(self, text: str) -> List[DrugInteraction]:
        """从文本中自动提取药物并检测交互"""
        entities = self._ner.extract(text)
        drugs = [e.text for e in entities if e.entity_type == EntityType.DRUG]
        return self._drug_detector.detect(drugs)

    def analyze(
        self,
        text: str,
        options: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """
        综合分析文本（一次性执行所有分析）

        Args:
            text: 输入文本
            options: 分析选项，默认全部开启
                - ner: NER实体识别
                - pii: PII脱敏
                - summary: 文本摘要
                - relations: 关系抽取
                - drug_interaction: 药物交互检测
                - keywords: 关键词提取
                - sentiment: 情感分析
                - classification: 文本分类

        Returns:
            综合分析结果字典
        """
        if options is None:
            options = {
                "ner": True,
                "pii": True,
                "summary": True,
                "relations": True,
                "drug_interaction": True,
                "keywords": True,
                "sentiment": True,
                "classification": True,
            }

        result: Dict[str, Any] = {"text": text, "analyses": {}}

        if options.get("ner", False):
            entities = self._ner.extract(text)
            result["analyses"]["entities"] = [e.to_dict() for e in entities]
            result["analyses"]["entity_count"] = len(entities)

        if options.get("pii", False):
            pii_result = self._pii.sanitize(text)
            result["analyses"]["pii"] = pii_result.to_dict()

        if options.get("summary", False):
            result["analyses"]["summary"] = self._summarizer.summarize(text)

        if options.get("relations", False):
            entities = self._ner.extract(text)
            relations = self._relation_extractor.extract(text, entities)
            result["analyses"]["relations"] = [r.to_dict() for r in relations]

        if options.get("drug_interaction", False):
            entities = self._ner.extract(text)
            drugs = [e.text for e in entities if e.entity_type == EntityType.DRUG]
            interactions = self._drug_detector.detect(drugs)
            result["analyses"]["drug_interactions"] = [
                i.to_dict() for i in interactions
            ]

        if options.get("keywords", False):
            keywords = self._summarizer.extract_keywords(text)
            result["analyses"]["keywords"] = [
                {"word": w, "score": s} for w, s in keywords
            ]

        if options.get("sentiment", False):
            result["analyses"]["sentiment"] = self._summarizer.analyze_sentiment(text)

        if options.get("classification", False):
            result["analyses"]["classification"] = self._summarizer.classify_text(text)

        return result
