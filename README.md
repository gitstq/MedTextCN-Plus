# MedTextCN-Plus: 中文医疗文本智能分析引擎 Pro

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/Code%20Style-Black-black.svg)](https://github.com/psf/black)

> 轻量级中文医疗文本智能分析引擎 Pro 版 — NER实体识别 | PII隐私脱敏 | 智能摘要 | 关系抽取 | 药物交互检测 | 多模型支持 | 零外部依赖核心

## 🎉 项目介绍

MedTextCN-Plus 是一款专为中文医疗场景设计的轻量级文本智能分析引擎。它提供从基础文本处理到高级医疗AI分析的完整工具链，支持离线运行、保护患者隐私，适用于医疗信息化、临床研究、健康科技等领域。

与通用医疗AI工具不同，MedTextCN-Plus 深度优化了中文医疗文本的特殊需求：中文分词、医疗实体识别、患者隐私信息脱敏、药物交互检测等。

## ✨ 核心特性

- **🩺 医疗NER实体识别** — 识别疾病、症状、药物、检查项目、身体部位等8大类医疗实体
- **🔒 PII隐私脱敏** — 自动检测并脱敏患者姓名、身份证号、手机号、地址等敏感信息
- **📝 智能文本摘要** — 基于抽取式方法的中文医疗文本自动摘要生成
- **🔗 医疗关系抽取** — 识别药物-疾病、症状-疾病、药物-症状等实体间关系
- **💊 药物交互检测** — 检测药物间的潜在交互作用与禁忌
- **📊 多维度文本分析** — 情感分析、关键词提取、文本分类、相似度计算
- **🧠 多模型后端** — 支持规则引擎、TF-IDF、Word2Vec、BERT等多种分析后端
- **🖥️ 交互式TUI界面** — 美观的终端交互界面，支持实时分析
- **🌐 REST API服务** — 内置HTTP服务，支持远程调用
- **📦 零核心外部依赖** — 核心功能纯Python实现，可选依赖按需安装
- **🇨🇳 深度中文优化** — 专为中文医疗文本设计，支持简繁体中文

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/gitstq/MedTextCN-Plus.git
cd MedTextCN-Plus

# 安装依赖（核心功能零外部依赖）
pip install -e .

# 安装可选依赖（增强功能）
pip install -e ".[enhanced]"   # 增强分析功能
pip install -e ".[server]"     # REST API 服务
pip install -e ".[tui]"        # TUI 界面
pip install -e ".[all]"        # 全部功能
```

### 基础使用

```python
from medtextcn_plus import MedTextAnalyzer

# 初始化分析引擎
analyzer = MedTextAnalyzer()

# 分析医疗文本
text = "患者张三，男，45岁，因反复咳嗽、发热3天入院。既往有高血压病史，长期服用氨氯地平。查体：体温38.5°C，血压145/90mmHg。初步诊断：上呼吸道感染。处方：阿莫西林胶囊0.5g tid，布洛芬片0.2g prn。"

# NER实体识别
entities = analyzer.extract_entities(text)
for ent in entities:
    print(f"[{ent.entity_type}] {ent.text} (置信度: {ent.confidence:.2f})")

# PII隐私脱敏
sanitized = analyzer.sanitize_pii(text)
print(f"脱敏结果: {sanitized}")

# 智能摘要
summary = analyzer.summarize(text, max_length=50)
print(f"摘要: {summary}")

# 关系抽取
relations = analyzer.extract_relations(text)
for rel in relations:
    print(f"[{rel.relation_type}] {rel.subject} -> {rel.object}")

# 药物交互检测
interactions = analyzer.detect_drug_interactions(["阿莫西林", "布洛芬", "氨氯地平"])
for interaction in interactions:
    print(f"[{interaction.severity}] {interaction.drug_a} + {interaction.drug_b}: {interaction.description}")
```

### 命令行使用

```bash
# 分析文本文件
medtext analyze --input medical_report.txt --output results.json

# PII脱敏
medtext sanitize --input patient_data.txt --output sanitized.txt

# 批量处理
medtext batch --dir ./medical_records/ --output ./results/

# 启动API服务
medtext serve --host 0.0.0.0 --port 8080

# 启动TUI界面
medtext tui
```

## 📖 详细使用指南

### NER实体识别

支持8大类医疗实体：

| 实体类型 | 说明 | 示例 |
|---------|------|------|
| DISEASE | 疾病名称 | 高血压、糖尿病、上呼吸道感染 |
| SYMPTOM | 症状描述 | 咳嗽、发热、头痛 |
| DRUG | 药物名称 | 阿莫西林、布洛芬、氨氯地平 |
| TEST | 检查项目 | 血常规、CT、MRI |
| BODY_PART | 身体部位 | 肺部、肝脏、心脏 |
| TREATMENT | 治疗方案 | 手术、化疗、透析 |
| TIME | 时间表达 | 3天、2周、长期 |
| LAB_VALUE | 检验数值 | 38.5°C、145/90mmHg |

### PII隐私脱敏

自动识别并脱敏以下敏感信息：
- 患者姓名 → `[患者]`
- 身份证号 → `[身份证]`
- 手机号码 → `[手机号]`
- 家庭住址 → `[地址]`
- 医保卡号 → `[医保卡号]`
- 就诊卡号 → `[就诊卡号]`

### REST API

```bash
# 启动服务
medtext serve --port 8080

# API 调用示例
curl -X POST http://localhost:8080/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "患者因反复咳嗽入院...", "options": {"ner": true, "pii": true, "summary": true}}'
```

## 💡 设计思路与迭代规划

### 设计理念

1. **隐私优先** — 所有核心分析在本地完成，不上传任何数据
2. **渐进增强** — 核心功能零依赖，高级功能可选安装
3. **中文优先** — 深度优化中文医疗文本处理
4. **模块化设计** — 每个分析模块独立可用，自由组合

### 迭代规划

- [x] v1.0 — 核心NER、PII脱敏、文本摘要
- [x] v1.1 — 关系抽取、药物交互检测
- [x] v1.2 — REST API、TUI界面
- [ ] v2.0 — 集成BERT/Transformers模型
- [ ] v2.1 — 电子病历结构化解析
- [ ] v3.0 — 多模态医疗影像分析

## 📦 打包与部署

```bash
# 安装打包工具
pip install build

# 构建
python -m build

# 生成的包在 dist/ 目录下
# medtextcn_plus-1.2.0-py3-none-any.whl
# medtextcn_plus-1.2.0.tar.gz

# Docker 部署
docker build -t medtextcn-plus .
docker run -p 8080:8080 medtextcn-plus
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

提交规范请遵循 [Conventional Commits](https://www.conventionalcommits.org/)。

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

**⚠️ 免责声明**：本工具仅供学术研究和技术学习使用，不构成任何医疗建议或诊断依据。在实际医疗场景中使用前，请务必进行专业验证和合规审查。
