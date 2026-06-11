"""药物交互检测器 — 检测药物间的潜在交互作用"""

from typing import List, Dict, Tuple, Optional

from medtextcn_plus.models.drug import (
    DrugInteraction,
    DrugInfo,
    InteractionSeverity,
    InteractionType,
)


# 内置药物交互知识库
_DRUG_INTERACTIONS: List[Dict] = [
    # 严重交互
    {
        "drug_a": "华法林",
        "drug_b": "阿司匹林",
        "severity": "critical",
        "type": "pharmacodynamic",
        "description": "同时使用显著增加出血风险",
        "mechanism": "两者均抑制血小板功能并影响凝血级联",
        "recommendation": "避免同时使用，如必须联用需密切监测INR和出血征象",
        "evidence": "established",
    },
    {
        "drug_a": "华法林",
        "drug_b": "布洛芬",
        "severity": "major",
        "type": "pharmacodynamic",
        "description": "增加出血风险并可能减弱抗凝效果",
        "mechanism": "NSAIDs抑制血小板并可能影响华法林蛋白结合",
        "recommendation": "避免联用，考虑替代方案如对乙酰氨基酚",
        "evidence": "established",
    },
    {
        "drug_a": "卡托普利",
        "drug_b": "螺内酯",
        "severity": "major",
        "type": "pharmacodynamic",
        "description": "双重阻断RAAS系统，高钾血症风险显著增加",
        "mechanism": "ACEI减少醛固酮分泌，螺内酯拮抗醛固酮，共同导致钾潴留",
        "recommendation": "如需联用需密切监测血钾和肾功能",
        "evidence": "established",
    },
    {
        "drug_a": "地高辛",
        "drug_b": "胺碘酮",
        "severity": "major",
        "type": "pharmacokinetic",
        "description": "胺碘酮升高地高辛血药浓度，增加中毒风险",
        "mechanism": "胺碘酮抑制P-gp转运体，减少地高辛清除",
        "recommendation": "联用时地高辛剂量减半，监测血药浓度",
        "evidence": "established",
    },
    # 中等交互
    {
        "drug_a": "氨氯地平",
        "drug_b": "辛伐他汀",
        "severity": "moderate",
        "type": "pharmacokinetic",
        "description": "氨氯地平升高辛伐他汀血药浓度",
        "mechanism": "CYP3A4抑制导致辛伐他汀代谢减慢",
        "recommendation": "辛伐他汀日剂量不超过20mg",
        "evidence": "established",
    },
    {
        "drug_a": "二甲双胍",
        "drug_b": "造影剂",
        "severity": "moderate",
        "type": "pharmacodynamic",
        "description": "联用增加乳酸酸中毒风险",
        "mechanism": "造影剂可能导致急性肾损伤，影响二甲双胍排泄",
        "recommendation": "造影前48h停用二甲双胍，造影后48h确认肾功能正常后恢复",
        "evidence": "established",
    },
    {
        "drug_a": "阿莫西林",
        "drug_b": "甲硝唑",
        "severity": "minor",
        "type": "pharmacodynamic",
        "description": "联用对厌氧菌感染有协同作用",
        "mechanism": "不同抗菌机制互补",
        "recommendation": "可安全联用，注意胃肠道反应",
        "evidence": "established",
    },
    {
        "drug_a": "布洛芬",
        "drug_b": "阿司匹林",
        "severity": "moderate",
        "type": "pharmacodynamic",
        "description": "布洛芬可能减弱阿司匹林的心脏保护作用",
        "mechanism": "布洛芬竞争性结合COX-1，阻止阿司匹林不可逆抑制",
        "recommendation": "如需联用，至少间隔2小时服用",
        "evidence": "probable",
    },
    {
        "drug_a": "奥美拉唑",
        "drug_b": "氯吡格雷",
        "severity": "moderate",
        "type": "pharmacokinetic",
        "description": "奥美拉唑降低氯吡格雷抗血小板活性",
        "mechanism": "CYP2C19竞争抑制，减少氯吡格雷活性代谢物生成",
        "recommendation": "避免联用，可换用泮托拉唑",
        "evidence": "established",
    },
    {
        "drug_a": "美托洛尔",
        "drug_b": "维拉帕米",
        "severity": "critical",
        "type": "pharmacodynamic",
        "description": "联用可能导致严重心动过缓和低血压",
        "mechanism": "双重抑制心脏传导和心肌收缩力",
        "recommendation": "禁止静脉联用，口服联用需极度谨慎",
        "evidence": "established",
    },
    {
        "drug_a": "呋塞米",
        "drug_b": "氨基糖苷类",
        "severity": "major",
        "type": "pharmacodynamic",
        "description": "增加耳毒性和肾毒性风险",
        "mechanism": "呋塞米引起的电解质紊乱加重氨基糖苷类的毒性",
        "recommendation": "避免联用，如必须联用需密切监测听力和肾功能",
        "evidence": "established",
    },
    {
        "drug_a": "泼尼松",
        "drug_b": "布洛芬",
        "severity": "moderate",
        "type": "pharmacodynamic",
        "description": "增加胃肠道溃疡和出血风险",
        "mechanism": "糖皮质激素减弱胃黏膜保护，NSAIDs损伤胃黏膜",
        "recommendation": "联用时加用胃黏膜保护剂",
        "evidence": "established",
    },
]


class DrugInteractionDetector:
    """药物交互检测器"""

    def __init__(self):
        """初始化检测器"""
        self._interaction_db = self._build_interaction_db()

    def detect(self, drugs: List[str]) -> List[DrugInteraction]:
        """
        检测药物列表中的交互作用

        Args:
            drugs: 药物名称列表

        Returns:
            药物交互列表
        """
        interactions = []
        seen = set()

        for i, drug_a in enumerate(drugs):
            for j, drug_b in enumerate(drugs):
                if i >= j:
                    continue

                key = tuple(sorted([drug_a, drug_b]))
                if key in seen:
                    continue
                seen.add(key)

                found = self._lookup_interaction(drug_a, drug_b)
                if found:
                    interactions.append(found)

        # 按严重程度排序
        severity_order = {
            InteractionSeverity.CRITICAL: 0,
            InteractionSeverity.MAJOR: 1,
            InteractionSeverity.MODERATE: 2,
            InteractionSeverity.MINOR: 3,
        }
        interactions.sort(key=lambda x: severity_order.get(x.severity, 4))
        return interactions

    def get_drug_info(self, drug_name: str) -> Optional[DrugInfo]:
        """获取药物详细信息"""
        return None  # 可扩展

    def _lookup_interaction(
        self, drug_a: str, drug_b: str
    ) -> Optional[DrugInteraction]:
        """查找两个药物间的交互"""
        for entry in _DRUG_INTERACTIONS:
            if (drug_a in entry["drug_a"] or entry["drug_a"] in drug_a) and \
               (drug_b in entry["drug_b"] or entry["drug_b"] in drug_b):
                return DrugInteraction(
                    drug_a=entry["drug_a"],
                    drug_b=entry["drug_b"],
                    severity=InteractionSeverity(entry["severity"]),
                    interaction_type=InteractionType(entry["type"]),
                    description=entry["description"],
                    mechanism=entry["mechanism"],
                    recommendation=entry["recommendation"],
                    evidence_level=entry["evidence"],
                )
            # 反向匹配
            if (drug_b in entry["drug_a"] or entry["drug_a"] in drug_b) and \
               (drug_a in entry["drug_b"] or entry["drug_b"] in drug_a):
                return DrugInteraction(
                    drug_a=entry["drug_a"],
                    drug_b=entry["drug_b"],
                    severity=InteractionSeverity(entry["severity"]),
                    interaction_type=InteractionType(entry["type"]),
                    description=entry["description"],
                    mechanism=entry["mechanism"],
                    recommendation=entry["recommendation"],
                    evidence_level=entry["evidence"],
                )
        return None

    def _build_interaction_db(self) -> Dict:
        """构建交互数据库索引"""
        db = {}
        for entry in _DRUG_INTERACTIONS:
            for drug_key in [entry["drug_a"], entry["drug_b"]]:
                if drug_key not in db:
                    db[drug_key] = []
                db[drug_key].append(entry)
        return db
