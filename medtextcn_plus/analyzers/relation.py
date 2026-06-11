"""医疗关系抽取器 — 识别医疗实体间的关系"""

import re
from typing import List, Dict, Tuple, Optional

from medtextcn_plus.models.entities import Entity, EntityType, Relation, RelationType
from medtextcn_plus.utils.text import extract_sentences


# 关系模式定义
_RELATION_PATTERNS: Dict[RelationType, List[str]] = {
    RelationType.DRUG_TREATS_DISEASE: [
        r"用{drug}治疗{disease}",
        r"{drug}治疗{disease}",
        r"{drug}用于{disease}",
        r"处方{drug}.*?{disease}",
        r"{drug}.*?治疗{disease}",
        r"服用{drug}.*?{disease}",
    ],
    RelationType.DRUG_TREATS_SYMPTOM: [
        r"{drug}缓解{symptom}",
        r"用{drug}.*?{symptom}",
        r"{drug}.*?止痛|退热|止咳",
        r"服用{drug}.*?{symptom}",
    ],
    RelationType.DISEASE_CAUSES_SYMPTOM: [
        r"{disease}.*?出现{symptom}",
        r"{disease}.*?伴{symptom}",
        r"{disease}.*?导致{symptom}",
        r"{disease}.*?引起{symptom}",
        r"因{disease}.*?{symptom}",
        r"{disease}.*?表现为{symptom}",
    ],
    RelationType.DISEASE_AFFECTS_BODY: [
        r"{disease}.*?累及{body}",
        r"{disease}.*?侵犯{body}",
        r"{disease}.*?转移至{body}",
        r"{body}.*?{disease}",
    ],
    RelationType.TEST_DETECTS_DISEASE: [
        r"{test}.*?提示{disease}",
        r"{test}.*?发现{disease}",
        r"{test}.*?确诊{disease}",
        r"{test}.*?排除{disease}",
        r"经{test}.*?诊断为{disease}",
    ],
    RelationType.SYMPTOM_OF_DISEASE: [
        r"{symptom}.*?考虑{disease}",
        r"{symptom}.*?疑似{disease}",
        r"以{symptom}.*?为表现的{disease}",
    ],
}

# 关键词映射
_RELATION_KEYWORDS: Dict[RelationType, List[str]] = {
    RelationType.DRUG_TREATS_DISEASE: [
        "治疗", "治愈", "控制", "用于", "处方", "给药",
    ],
    RelationType.DRUG_TREATS_SYMPTOM: [
        "缓解", "止痛", "退热", "止咳", "止吐", "消炎",
    ],
    RelationType.DISEASE_CAUSES_SYMPTOM: [
        "导致", "引起", "出现", "伴有", "表现为", "并发",
    ],
    RelationType.DISEASE_AFFECTS_BODY: [
        "累及", "侵犯", "转移", "浸润", "扩散",
    ],
    RelationType.TEST_DETECTS_DISEASE: [
        "提示", "发现", "确诊", "诊断", "排除", "考虑",
    ],
}

# 实体类型到关系角色的映射
_ENTITY_ROLE_MAP: Dict[RelationType, Tuple[EntityType, EntityType]] = {
    RelationType.DRUG_TREATS_DISEASE: (EntityType.DRUG, EntityType.DISEASE),
    RelationType.DRUG_TREATS_SYMPTOM: (EntityType.DRUG, EntityType.SYMPTOM),
    RelationType.DISEASE_CAUSES_SYMPTOM: (EntityType.DISEASE, EntityType.SYMPTOM),
    RelationType.DISEASE_AFFECTS_BODY: (EntityType.DISEASE, EntityType.BODY_PART),
    RelationType.TEST_DETECTS_DISEASE: (EntityType.TEST, EntityType.DISEASE),
    RelationType.SYMPTOM_OF_DISEASE: (EntityType.SYMPTOM, EntityType.DISEASE),
}


class RelationExtractor:
    """医疗实体关系抽取器"""

    def __init__(self):
        """初始化关系抽取器"""
        self._window_size = 30  # 关系抽取窗口大小（字符数）

    def extract(self, text: str, entities: List[Entity]) -> List[Relation]:
        """
        从文本和实体列表中抽取关系

        Args:
            text: 原始文本
            entities: 已识别的实体列表

        Returns:
            关系列表
        """
        relations = []

        # 按句子处理
        sentences = extract_sentences(text)
        for sentence in sentences:
            sent_entities = self._filter_entities_in_range(
                entities, text.find(sentence), text.find(sentence) + len(sentence)
            )
            sent_relations = self._extract_from_sentence(sentence, sent_entities)
            relations.extend(sent_relations)

        return relations

    def _extract_from_sentence(
        self, sentence: str, entities: List[Entity]
    ) -> List[Relation]:
        """从单个句子中抽取关系"""
        relations = []

        for rel_type, (subj_type, obj_type) in _ENTITY_ROLE_MAP.items():
            subj_entities = [e for e in entities if e.entity_type == subj_type]
            obj_entities = [e for e in entities if e.entity_type == obj_type]

            for subj in subj_entities:
                for obj in obj_entities:
                    # 检查两个实体是否在窗口范围内
                    distance = abs(subj.end - obj.start)
                    if distance > self._window_size:
                        continue

                    # 检查是否存在关系关键词
                    between_text = sentence[min(subj.end, obj.end):max(subj.start, obj.start)]
                    keywords = _RELATION_KEYWORDS.get(rel_type, [])
                    has_keyword = any(kw in between_text for kw in keywords)

                    if has_keyword:
                        relations.append(Relation(
                            subject=subj,
                            object=obj,
                            relation_type=rel_type,
                            confidence=0.75,
                            evidence=between_text.strip(),
                        ))

        return relations

    def _filter_entities_in_range(
        self, entities: List[Entity], start: int, end: int
    ) -> List[Entity]:
        """筛选在指定范围内的实体"""
        return [e for e in entities if e.start >= start and e.end <= end]
