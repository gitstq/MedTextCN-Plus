"""MedTextCN-Plus 单元测试"""

import json
import pytest
from pathlib import Path

from medtextcn_plus import MedTextAnalyzer
from medtextcn_plus.models.entities import Entity, EntityType, Relation, RelationType
from medtextcn_plus.models.pii import PIIMatch, PIIType, SanitizationResult
from medtextcn_plus.models.drug import DrugInteraction, InteractionSeverity
from medtextcn_plus.analyzers.ner import MedicalNER
from medtextcn_plus.analyzers.pii import PIIDetector
from medtextcn_plus.analyzers.summary import TextSummarizer
from medtextcn_plus.analyzers.relation import RelationExtractor
from medtextcn_plus.analyzers.drug import DrugInteractionDetector
from medtextcn_plus.utils.text import (
    is_chinese_char,
    contains_chinese,
    normalize_text,
    simple_tokenize,
    extract_sentences,
    calculate_text_similarity,
    detect_text_language,
)


# 测试用医疗文本
SAMPLE_TEXT = (
    "患者张三，男，45岁，因反复咳嗽、发热3天入院。"
    "既往有高血压病史，长期服用氨氯地平。"
    "查体：体温38.5°C，血压145/90mmHg。"
    "初步诊断：上呼吸道感染。"
    "处方：阿莫西林胶囊0.5g tid，布洛芬片0.2g prn。"
)

SAMPLE_TEXT_WITH_ADDRESS = (
    "患者李四，女，32岁，住北京市朝阳区建国路88号。"
    "因头痛、头晕就诊。联系电话13800138000。"
    "身份证号110105199203150023。"
    "诊断：偏头痛。处方：布洛芬片0.2g prn。"
)


class TestUtils:
    """工具函数测试"""

    def test_is_chinese_char(self):
        assert is_chinese_char("中") is True
        assert is_chinese_char("A") is False
        assert is_chinese_char("1") is False

    def test_contains_chinese(self):
        assert contains_chinese("你好世界") is True
        assert contains_chinese("Hello World") is False
        assert contains_chinese("Hello 世界") is True

    def test_normalize_text(self):
        assert normalize_text("  你好　世界  ") == "你好 世界"
        assert normalize_text("ＡＢＣ") == "ABC"

    def test_simple_tokenize(self):
        tokens = simple_tokenize("高血压患者")
        assert len(tokens) > 0
        assert any("高血压" in t for t in tokens)

    def test_extract_sentences(self):
        sentences = extract_sentences("你好。世界！测试")
        assert len(sentences) >= 2

    def test_calculate_text_similarity(self):
        sim = calculate_text_similarity("高血压", "高血压病")
        assert 0 < sim <= 1

    def test_detect_text_language(self):
        assert detect_text_language("这是中文") == "zh"
        assert detect_text_language("This is English") == "en"


class TestNER:
    """NER实体识别测试"""

    def setup_method(self):
        self.ner = MedicalNER()

    def test_extract_disease(self):
        entities = self.ner.extract("患者诊断为高血压和糖尿病")
        types = [e.entity_type for e in entities]
        assert EntityType.DISEASE in types

    def test_extract_symptom(self):
        entities = self.ner.extract("患者出现咳嗽、发热症状")
        types = [e.entity_type for e in entities]
        assert EntityType.SYMPTOM in types

    def test_extract_drug(self):
        entities = self.ner.extract("处方阿莫西林和布洛芬")
        types = [e.entity_type for e in entities]
        assert EntityType.DRUG in types

    def test_extract_body_part(self):
        entities = self.ner.extract("肝脏和肾脏功能正常")
        types = [e.entity_type for e in entities]
        assert EntityType.BODY_PART in types

    def test_extract_test(self):
        entities = self.ner.extract("血常规和肝功能检查")
        types = [e.entity_type for e in entities]
        assert EntityType.TEST in types

    def test_extract_lab_value(self):
        entities = self.ner.extract("体温38.5°C，血压145/90mmHg")
        types = [e.entity_type for e in entities]
        assert EntityType.LAB_VALUE in types

    def test_extract_comprehensive(self):
        entities = self.ner.extract(SAMPLE_TEXT)
        types = [e.entity_type for e in entities]
        assert EntityType.DISEASE in types
        assert EntityType.SYMPTOM in types
        assert EntityType.DRUG in types

    def test_entity_to_dict(self):
        entity = Entity(text="高血压", entity_type=EntityType.DISEASE, confidence=0.9)
        d = entity.to_dict()
        assert d["text"] == "高血压"
        assert d["type"] == "disease"


class TestPII:
    """PII脱敏测试"""

    def setup_method(self):
        self.detector = PIIDetector()

    def test_detect_phone(self):
        matches = self.detector.detect("联系电话13800138000")
        types = [m.pii_type for m in matches]
        assert PIIType.PHONE in types

    def test_detect_id_card(self):
        matches = self.detector.detect("身份证号110105199203150023")
        types = [m.pii_type for m in matches]
        assert PIIType.ID_CARD in types

    def test_detect_email(self):
        matches = self.detector.detect("邮箱test@example.com")
        types = [m.pii_type for m in matches]
        assert PIIType.EMAIL in types

    def test_sanitize(self):
        result = self.detector.sanitize("联系电话13800138000")
        assert "13800138000" not in result.sanitized_text
        assert "[手机号]" in result.sanitized_text

    def test_sanitize_result(self):
        result = self.detector.sanitize(SAMPLE_TEXT_WITH_ADDRESS)
        assert isinstance(result, SanitizationResult)
        assert result.pii_count > 0


class TestSummary:
    """文本摘要测试"""

    def setup_method(self):
        self.summarizer = TextSummarizer()

    def test_summarize(self):
        summary = self.summarizer.summarize(SAMPLE_TEXT, max_length=50)
        assert len(summary) <= 55  # 允许"..."额外字符
        assert len(summary) > 0

    def test_extract_keywords(self):
        keywords = self.summarizer.extract_keywords(SAMPLE_TEXT, top_n=5)
        assert len(keywords) > 0
        assert len(keywords) <= 5

    def test_analyze_sentiment(self):
        result = self.summarizer.analyze_sentiment(SAMPLE_TEXT)
        assert "positive" in result
        assert "negative" in result
        assert "overall" in result

    def test_classify_text(self):
        result = self.summarizer.classify_text(SAMPLE_TEXT)
        assert isinstance(result, dict)


class TestRelation:
    """关系抽取测试"""

    def setup_method(self):
        self.extractor = RelationExtractor()

    def test_extract_relations(self):
        text = "患者因高血压出现头痛症状，服用氨氯地平治疗高血压"
        ner = MedicalNER()
        entities = ner.extract(text)
        relations = self.extractor.extract(text, entities)
        # 至少应有一些关系被识别
        assert isinstance(relations, list)


class TestDrugInteraction:
    """药物交互检测测试"""

    def setup_method(self):
        self.detector = DrugInteractionDetector()

    def test_detect_interaction(self):
        interactions = self.detector.detect(["华法林", "阿司匹林"])
        assert len(interactions) > 0
        assert interactions[0].severity == InteractionSeverity.CRITICAL

    def test_no_interaction(self):
        interactions = self.detector.detect(["阿莫西林", "维生素"])
        # 可能没有交互或只有轻微交互
        for i in interactions:
            assert i.severity in [InteractionSeverity.MINOR, InteractionSeverity.NONE]

    def test_detect_from_text(self):
        interactions = self.detector.detect(["布洛芬", "华法林"])
        assert len(interactions) > 0


class TestEngine:
    """核心引擎集成测试"""

    def setup_method(self):
        self.analyzer = MedTextAnalyzer()

    def test_extract_entities(self):
        entities = self.analyzer.extract_entities(SAMPLE_TEXT)
        assert len(entities) > 0

    def test_sanitize_pii(self):
        sanitized = self.analyzer.sanitize_pii(SAMPLE_TEXT)
        assert isinstance(sanitized, str)

    def test_sanitize_pii_full(self):
        result = self.analyzer.sanitize_pii_full(SAMPLE_TEXT_WITH_ADDRESS)
        assert isinstance(result, SanitizationResult)
        assert result.pii_count > 0

    def test_summarize(self):
        summary = self.analyzer.summarize(SAMPLE_TEXT)
        assert len(summary) > 0

    def test_extract_keywords(self):
        keywords = self.analyzer.extract_keywords(SAMPLE_TEXT)
        assert len(keywords) > 0

    def test_extract_relations(self):
        relations = self.analyzer.extract_relations(SAMPLE_TEXT)
        assert isinstance(relations, list)

    def test_detect_drug_interactions(self):
        interactions = self.analyzer.detect_drug_interactions(["华法林", "阿司匹林"])
        assert len(interactions) > 0

    def test_analyze_comprehensive(self):
        result = self.analyzer.analyze(SAMPLE_TEXT)
        assert "analyses" in result
        assert "entities" in result["analyses"]

    def test_analyze_with_options(self):
        result = self.analyzer.analyze(SAMPLE_TEXT, {"ner": True, "pii": False})
        assert "entities" in result["analyses"]
        assert "pii" not in result["analyses"] or result["analyses"]["pii"]["pii_count"] == 0

    def test_empty_text(self):
        entities = self.analyzer.extract_entities("")
        assert entities == []

    def test_non_medical_text(self):
        entities = self.analyzer.extract_entities("今天天气真好")
        assert isinstance(entities, list)


class TestModels:
    """数据模型测试"""

    def test_entity_creation(self):
        e = Entity(text="高血压", entity_type=EntityType.DISEASE)
        assert e.text == "高血压"
        assert e.confidence == 1.0

    def test_relation_creation(self):
        subj = Entity(text="阿莫西林", entity_type=EntityType.DRUG)
        obj = Entity(text="肺炎", entity_type=EntityType.DISEASE)
        r = Relation(subject=subj, object=obj, relation_type=RelationType.DRUG_TREATS_DISEASE)
        assert "阿莫西林" in repr(r)

    def test_drug_interaction_creation(self):
        di = DrugInteraction(
            drug_a="华法林", drug_b="阿司匹林",
            severity=InteractionSeverity.CRITICAL,
            description="增加出血风险",
        )
        d = di.to_dict()
        assert d["severity"] == "critical"
