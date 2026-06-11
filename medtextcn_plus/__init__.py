"""
MedTextCN-Plus: 中文医疗文本智能分析引擎 Pro 版
Lightweight Chinese Medical Text Intelligence Engine Pro

核心功能：NER实体识别 | PII隐私脱敏 | 智能摘要 | 关系抽取 | 药物交互检测
"""

__version__ = "1.2.0"
__author__ = "MedTextCN-Plus Contributors"
__license__ = "MIT"

from medtextcn_plus.core.engine import MedTextAnalyzer
from medtextcn_plus.models.entities import Entity, EntityType, Relation, RelationType
from medtextcn_plus.models.pii import PIIMatch, PIIType
from medtextcn_plus.models.drug import DrugInteraction, InteractionSeverity

__all__ = [
    "MedTextAnalyzer",
    "Entity",
    "EntityType",
    "Relation",
    "RelationType",
    "PIIMatch",
    "PIIType",
    "DrugInteraction",
    "InteractionSeverity",
]
