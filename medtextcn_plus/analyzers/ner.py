"""医疗NER实体识别器 — 基于规则与词典的中文医疗实体识别"""

import re
from typing import List, Optional, Dict

from medtextcn_plus.models.entities import Entity, EntityType
from medtextcn_plus.utils.text import normalize_text, contains_chinese


# 内置医疗词典
_DISEASE_KEYWORDS: Dict[str, List[str]] = {
    "common": [
        "高血压", "糖尿病", "冠心病", "肺炎", "胃炎", "肝炎", "肾炎",
        "脑梗塞", "脑出血", "心肌梗塞", "心力衰竭", "心律失常", "哮喘",
        "支气管炎", "肺气肿", "肺结核", "肺癌", "胃癌", "肝癌", "结肠癌",
        "白血病", "贫血", "甲亢", "甲减", "骨质疏松", "关节炎", "痛风",
        "帕金森", "阿尔茨海默", "抑郁症", "焦虑症", "精神分裂", "癫痫",
        "甲状腺肿", "甲状腺炎", "肾炎综合征", "尿毒症", "前列腺炎",
        "宫颈炎", "子宫内膜异位", "卵巢囊肿", "乳腺增生", "乳腺纤维瘤",
        "青光眼", "白内障", "中耳炎", "鼻炎", "咽炎", "扁桃体炎",
        "阑尾炎", "胰腺炎", "胆囊炎", "胆结石", "肾结石", "输尿管结石",
        "痔疮", "静脉曲张", "湿疹", "荨麻疹", "银屑病", "带状疱疹",
        "上呼吸道感染", "下呼吸道感染", "泌尿系统感染", "败血症",
        "过敏性休克", "食物中毒", "一氧化碳中毒", "酒精中毒",
        "类风湿", "强直性脊柱炎", "红斑狼疮", "干燥综合征",
        "感冒", "流感", "手足口病", "水痘", "腮腺炎", "百日咳",
        "登革热", "疟疾", "结核病", "艾滋病", "梅毒", "淋病",
        "脂肪肝", "肝硬化", "肝脓肿", "腹膜炎", "肠梗阻",
        "脑膜炎", "脑炎", "脊髓炎", " Guillain-Barre",
        "骨质疏松症", "佝偻病", "败血病", "脓毒症",
        "代谢综合征", "高脂血症", "高尿酸血症", "低蛋白血症",
    ],
}

_SYMPTOM_KEYWORDS: List[str] = [
    "咳嗽", "发热", "头痛", "头晕", "恶心", "呕吐", "腹泻", "便秘",
    "腹痛", "胸痛", "背痛", "关节痛", "肌肉痛", "乏力", "疲劳",
    "失眠", "嗜睡", "多汗", "盗汗", "食欲不振", "消瘦", "肥胖",
    "水肿", "呼吸困难", "气短", "心悸", "胸闷", "气促",
    "尿频", "尿急", "尿痛", "血尿", "蛋白尿",
    "皮疹", "瘙痒", "出血", "淤血", "黄疸",
    "视力模糊", "耳鸣", "听力下降", "鼻塞", "流涕",
    "口干", "口苦", "口腔溃疡", "吞咽困难",
    "抽搐", "震颤", "麻木", "刺痛", "灼痛",
    "反酸", "烧心", "腹胀", "嗳气",
    "畏寒", "寒战", "潮热", "面色苍白",
    "反复咳嗽", "持续发热", "阵发性头痛",
    "活动后气促", "夜间阵发性呼吸困难",
    "间歇性跛行", "静息痛",
]

_DRUG_KEYWORDS: List[str] = [
    # 常见西药
    "阿莫西林", "阿奇霉素", "头孢克肟", "头孢呋辛", "左氧氟沙星",
    "莫西沙星", "青霉素", "红霉素", "克林霉素", "甲硝唑",
    "布洛芬", "对乙酰氨基酚", "阿司匹林", "双氯芬酸", "塞来昔布",
    "氨氯地平", "硝苯地平", "缬沙坦", "氯沙坦", "依那普利",
    "卡托普利", "培哚普利", "美托洛尔", "比索洛尔", "阿替洛尔",
    "二甲双胍", "格列美脲", "阿卡波糖", "胰岛素", "吡格列酮",
    "辛伐他汀", "阿托伐他汀", "瑞舒伐他汀", "普伐他汀",
    "奥美拉唑", "兰索拉唑", "泮托拉唑", "雷贝拉唑",
    "氯雷他定", "西替利嗪", "孟鲁司特", "扑尔敏",
    "地塞米松", "泼尼松", "甲泼尼龙", "氢化可的松",
    "华法林", "利伐沙班", "氯吡格雷", "阿替普酶",
    "氨茶碱", "沙丁胺醇", "布地奈德", "异丙托溴铵",
    "地高辛", "胺碘酮", "普罗帕酮", "维拉帕米",
    "呋塞米", "螺内酯", "氢氯噻嗪", "吲达帕胺",
    "奥司他韦", "利巴韦林", "阿昔洛韦", "更昔洛韦",
    "氟康唑", "伊曲康唑", "伏立康唑",
    "蒙脱石散", "双歧杆菌", "乳酸菌素",
    "碳酸氢钠", "氯化钾", "葡萄糖酸钙",
    "维生素C", "维生素B", "维生素D", "钙片",
    "复方甘草片", "急支糖浆", "川贝枇杷膏",
    "藿香正气水", "板蓝根", "连花清瘟",
    # 中成药
    "六味地黄丸", "逍遥丸", "归脾丸", "补中益气丸",
    "金匮肾气丸", "桂枝茯苓丸", "血府逐瘀汤",
    "安宫牛黄丸", "紫雪丹", "至宝丹",
]

_TEST_KEYWORDS: List[str] = [
    "血常规", "尿常规", "便常规", "肝功能", "肾功能", "血脂",
    "血糖", "糖化血红蛋白", "凝血功能", "电解质", "血气分析",
    "心电图", "超声心动图", "胸片", "CT", "MRI", "PET-CT",
    "B超", "彩超", "腹部超声", "心脏超声",
    "胃镜", "肠镜", "支气管镜", "腹腔镜",
    "病理检查", "细胞学检查", "免疫组化",
    "血培养", "药敏试验", "核酸检测", "PCR",
    "肿瘤标志物", "CEA", "AFP", "CA125", "CA199",
    "甲状腺功能", "T3", "T4", "TSH",
    "激素水平", "皮质醇", "醛固酮",
    "肺功能检查", "支气管激发试验",
    "眼底检查", "视野检查", "OCT",
    "骨密度检查", "关节穿刺",
    "脑电图", "肌电图", "神经传导速度",
    "Holter", "动态心电图", "运动平板试验",
    "冠脉造影", "冠脉CTA",
]

_BODY_PART_KEYWORDS: List[str] = [
    "头部", "面部", "眼部", "耳部", "鼻部", "口腔", "咽喉",
    "颈部", "胸部", "乳房", "腹部", "背部", "腰部", "脊柱",
    "上肢", "下肢", "手部", "足部", "肩部", "肘部", "腕部",
    "髋部", "膝部", "踝部",
    "心脏", "肺部", "肝脏", "脾脏", "胆囊", "胰腺",
    "肾脏", "膀胱", "前列腺", "子宫", "卵巢", "输卵管",
    "胃", "小肠", "大肠", "直肠", "阑尾",
    "甲状腺", "肾上腺", "垂体",
    "大脑", "小脑", "脑干", "脊髓",
    "血管", "动脉", "静脉", "淋巴结",
    "皮肤", "黏膜", "骨骼", "肌肉", "关节",
    "左心室", "右心室", "左心房", "右心房",
    "冠状动脉", "主动脉", "颈动脉",
]

_TREATMENT_KEYWORDS: List[str] = [
    "手术", "切除术", "移植术", "置换术", "修复术",
    "化疗", "放疗", "靶向治疗", "免疫治疗", "内分泌治疗",
    "透析", "血液透析", "腹膜透析",
    "介入治疗", "支架植入", "球囊扩张",
    "消融术", "栓塞术", "硬化治疗",
    "清创术", "缝合术", "引流术",
    "输液", "输血", "吸氧", "雾化吸入",
    "物理治疗", "康复训练", "言语治疗",
    "针灸", "推拿", "按摩", "拔罐", "艾灸",
    "体外碎石", "内镜下治疗",
    "心肺复苏", "气管插管", "机械通气",
]

_TIME_KEYWORDS: List[str] = [
    "天", "周", "月", "年", "小时", "分钟",
    "急性", "慢性", "持续性", "间歇性", "反复",
    "长期", "短期", "近期", "远期",
    "术前", "术后", "入院时", "出院时",
    "晨起", "夜间", "日间",
    "3天", "5天", "7天", "2周", "1月", "3月", "半年",
]

_LAB_VALUE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*[°℃%]\s*[CF]?"  # 温度/百分比
    r"|(\d+(?:\.\d+)?)\s*(?:mmHg|mmol/L|mg/dL|g/L|U/L|pg/mL|ng/mL|μmol/L|×10⁹/L|×10¹²/L)"
    r"|(\d+(?:\.\d+)?)\s*[/]\s*(\d+(?:\.\d+)?)\s*mmHg"  # 血压
)


class MedicalNER:
    """基于规则与词典的中文医疗NER识别器"""

    def __init__(self):
        """初始化NER识别器，构建词典树"""
        self._entity_type_map = {
            EntityType.DISEASE: _DISEASE_KEYWORDS["common"],
            EntityType.SYMPTOM: _SYMPTOM_KEYWORDS,
            EntityType.DRUG: _DRUG_KEYWORDS,
            EntityType.TEST: _TEST_KEYWORDS,
            EntityType.BODY_PART: _BODY_PART_KEYWORDS,
            EntityType.TREATMENT: _TREATMENT_KEYWORDS,
            EntityType.TIME: _TIME_KEYWORDS,
        }
        # 按长度降序排列，优先匹配长词
        for etype in self._entity_type_map:
            self._entity_type_map[etype].sort(key=len, reverse=True)

    def extract(self, text: str) -> List[Entity]:
        """从文本中提取医疗实体"""
        entities = []
        used_spans = set()  # 避免重叠

        for entity_type, keywords in self._entity_type_map.items():
            for keyword in keywords:
                start = 0
                while True:
                    idx = text.find(keyword, start)
                    if idx == -1:
                        break
                    end = idx + len(keyword)
                    # 检查是否与已有实体重叠
                    span = (idx, end)
                    if not any(
                        span[0] < existing[1] and span[1] > existing[0]
                        for existing in used_spans
                    ):
                        entities.append(Entity(
                            text=keyword,
                            entity_type=entity_type,
                            start=idx,
                            end=end,
                            confidence=0.85,
                        ))
                        used_spans.add(span)
                    start = idx + 1

        # 提取检验数值
        for match in _LAB_VALUE_PATTERN.finditer(text):
            span = (match.start(), match.end())
            if not any(
                span[0] < existing[1] and span[1] > existing[0]
                for existing in used_spans
            ):
                entities.append(Entity(
                    text=match.group(),
                    entity_type=EntityType.LAB_VALUE,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.90,
                ))
                used_spans.add(span)

        # 按位置排序
        entities.sort(key=lambda e: e.start)
        return entities

    def extract_with_context(self, text: str, context_window: int = 10) -> List[Entity]:
        """提取实体并附加上下文"""
        entities = self.extract(text)
        for entity in entities:
            ctx_start = max(0, entity.start - context_window)
            ctx_end = min(len(text), entity.end + context_window)
            entity.attributes["context"] = text[ctx_start:ctx_end]
        return entities
