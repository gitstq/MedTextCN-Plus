"""PII隐私信息脱敏器 — 自动检测并脱敏中文医疗文本中的敏感信息"""

import re
from typing import List, Optional

from medtextcn_plus.models.pii import PIIMatch, PIIType, SanitizationResult


# 常见中文姓氏
_COMMON_SURNAMES = (
    "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜"
    "戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐"
    "费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄"
    "和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁"
    "杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍"
    "虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚"
    "程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓"
    "牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙"
    "叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴郁胥能苍双"
    "闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍却璩桑桂濮牛寿通边扈燕冀郏浦尚农"
    "温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘"
    "匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空"
    "曾母沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公"
)

# 中文姓名模式（2-3字）
_NAME_PATTERN = re.compile(
    rf"[{_COMMON_SURNAMES}][\u4e00-\u9fff]{{1,2}}"
)

# 身份证号（18位）— 不使用\b，中文环境下不生效
_ID_CARD_PATTERN = re.compile(
    r"(?<![.\d])[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx](?![.\d])"
)

# 手机号（中国大陆）
_PHONE_PATTERN = re.compile(
    r"(?<![.\d])1[3-9]\d{9}(?![.\d])"
)

# 座机号
_LANDLINE_PATTERN = re.compile(
    r"(?<![.\d])(?:0\d{2,3}[-]?)?\d{7,8}(?![.\d])"
)

# 邮箱
_EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

# 地址关键词
_ADDRESS_KEYWORDS = [
    "省", "市", "区", "县", "镇", "乡", "村", "街道", "路", "号",
    "栋", "楼", "单元", "室", "幢", "层", "座", "小区", "花园",
    "广场", "大厦", "公寓", "弄", "胡同", "巷",
]

# 医保卡号模式
_MEDICAL_CARD_PATTERN = re.compile(
    r"\b(?:医保卡|社保卡|医保号)[：:号]?\s*\d{8,20}\b"
    r"|\b\d{8,20}(?:号)?(?:医保卡|社保卡)\b"
)

# 就诊卡号模式
_VISIT_CARD_PATTERN = re.compile(
    r"\b(?:就诊卡|门诊号|住院号|病历号)[：:号]?\s*\d{6,15}\b"
    r"|\b\d{6,15}(?:号)?(?:就诊卡|门诊号|住院号|病历号)\b"
)

# 出生日期模式
_BIRTHDATE_PATTERN = re.compile(
    r"\b(?:出生日期|出生|生日)[：:为]?\s*(?:19|20)\d{2}年(?:0[1-9]|1[0-2])月(?:0[1-9]|[12]\d|3[01])日?\b"
    r"|\b(?:19|20)\d{2}[-/.](?:0[1-9]|1[0-2])[-/.](?:0[1-9]|[12]\d|3[01])\b"
)

# 职业关键词
_OCCUPATION_KEYWORDS = [
    "工人", "农民", "教师", "医生", "护士", "工程师", "学生", "公务员",
    "司机", "厨师", "服务员", "销售", "会计", "律师", "警察", "军人",
    "退休", "无业", "个体", "自由职业", "白领", "企业家",
]


class PIIDetector:
    """PII隐私信息检测与脱敏器"""

    def __init__(self):
        """初始化PII检测器"""
        self._patterns = {
            PIIType.ID_CARD: _ID_CARD_PATTERN,
            PIIType.PHONE: _PHONE_PATTERN,
            PIIType.EMAIL: _EMAIL_PATTERN,
            PIIType.MEDICAL_CARD: _MEDICAL_CARD_PATTERN,
            PIIType.VISIT_CARD: _VISIT_CARD_PATTERN,
            PIIType.BIRTHDATE: _BIRTHDATE_PATTERN,
        }
        self._replacement_map = {
            PIIType.PATIENT_NAME: "[患者]",
            PIIType.ID_CARD: "[身份证号]",
            PIIType.PHONE: "[手机号]",
            PIIType.ADDRESS: "[地址]",
            PIIType.MEDICAL_CARD: "[医保卡号]",
            PIIType.VISIT_CARD: "[就诊卡号]",
            PIIType.EMAIL: "[邮箱]",
            PIIType.BIRTHDATE: "[出生日期]",
            PIIType.OCCUPATION: "[职业]",
        }

    def detect(self, text: str) -> List[PIIMatch]:
        """检测文本中的PII信息"""
        matches = []

        # 基于正则的检测
        for pii_type, pattern in self._patterns.items():
            for match in pattern.finditer(text):
                matches.append(PIIMatch(
                    text=match.group(),
                    pii_type=pii_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.90,
                    replacement=self._replacement_map.get(pii_type, "[已脱敏]"),
                ))

        # 姓名检测（排除常见非姓名场景）
        for match in _NAME_PATTERN.finditer(text):
            name = match.group()
            # 检查上下文是否为患者姓名
            context_start = max(0, match.start() - 5)
            context_end = min(len(text), match.end() + 5)
            context = text[context_start:context_end]
            if any(kw in context for kw in ["患者", "病人", "姓名", "名叫", "名为", "先生", "女士"]):
                matches.append(PIIMatch(
                    text=name,
                    pii_type=PIIType.PATIENT_NAME,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.80,
                    replacement=self._replacement_map[PIIType.PATIENT_NAME],
                ))

        # 地址检测
        for keyword in _ADDRESS_KEYWORDS:
            idx = 0
            while True:
                pos = text.find(keyword, idx)
                if pos == -1:
                    break
                # 提取地址片段
                addr_start = max(0, pos - 10)
                addr_end = min(len(text), pos + 5)
                addr_text = text[addr_start:addr_end]
                if len(addr_text) >= 4:
                    matches.append(PIIMatch(
                        text=addr_text,
                        pii_type=PIIType.ADDRESS,
                        start=addr_start,
                        end=addr_end,
                        confidence=0.70,
                        replacement=self._replacement_map[PIIType.ADDRESS],
                    ))
                idx = pos + 1

        # 去重（按位置）
        matches = self._deduplicate_matches(matches)
        return matches

    def sanitize(self, text: str) -> SanitizationResult:
        """对文本进行PII脱敏处理"""
        matches = self.detect(text)
        sanitized = text
        pii_count = 0

        # 从后往前替换，避免位置偏移
        for match in sorted(matches, key=lambda m: m.start, reverse=True):
            sanitized = sanitized[:match.start] + match.replacement + sanitized[match.end:]
            pii_count += 1

        original_length = len(text)
        sanitized_length = sum(
            len(m.replacement) for m in matches
        ) + (original_length - sum(m.end - m.start for m in matches) if matches else original_length)

        return SanitizationResult(
            original_text=text,
            sanitized_text=sanitized,
            pii_matches=matches,
            pii_count=pii_count,
            sanitization_rate=len(matches) / max(1, original_length) * 100,
        )

    def _deduplicate_matches(self, matches: List[PIIMatch]) -> List[PIIMatch]:
        """去除重叠的PII匹配"""
        if not matches:
            return matches
        matches.sort(key=lambda m: (m.start, -len(m.text)))
        result = [matches[0]]
        for match in matches[1:]:
            if match.start >= result[-1].end:
                result.append(match)
            elif len(match.text) > len(result[-1].text):
                result[-1] = match
        return result
