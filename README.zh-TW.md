# MedTextCN-Plus: 中文醫療文本智慧分析引擎 Pro

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 輕量級中文醫療文本智慧分析引擎 Pro 版 — NER實體識別 | PII隱私脫敏 | 智慧摘要 | 關係抽取 | 藥物交互檢測 | 多模型支援 | 零外部依賴核心

## 🎉 專案介紹

MedTextCN-Plus 是一款專為中文醫療場景設計的輕量級文本智慧分析引擎。它提供從基礎文本處理到高級醫療AI分析的完整工具鏈，支援離線運行、保護患者隱私，適用於醫療資訊化、臨床研究、健康科技等領域。

與通用醫療AI工具不同，MedTextCN-Plus 深度優化了中文醫療文本的特殊需求：中文分詞、醫療實體識別、患者隱私資訊脫敏、藥物交互檢測等。

## ✨ 核心特性

- **🩺 醫療NER實體識別** — 識別疾病、症狀、藥物、檢查項目、身體部位等8大類醫療實體
- **🔒 PII隱私脫敏** — 自動偵測並脫敏患者姓名、身分證號、手機號、地址等敏感資訊
- **📝 智慧文本摘要** — 基於抽取式方法的中文醫療文本自動摘要生成
- **🔗 醫療關係抽取** — 識別藥物-疾病、症狀-疾病、藥物-症狀等實體間關係
- **💊 藥物交互檢測** — 偵測藥物間的潛在交互作用與禁忌
- **📊 多維度文本分析** — 情感分析、關鍵詞提取、文本分類、相似度計算
- **🧠 多模型後端** — 支援規則引擎、TF-IDF、Word2Vec、BERT等多種分析後端
- **🖥️ 互動式TUI介面** — 美觀的終端互動介面，支援即時分析
- **🌐 REST API服務** — 內建HTTP服務，支援遠端呼叫
- **📦 零核心外部依賴** — 核心功能純Python實現，可選依賴按需安裝
- **🇨🇳 深度中文優化** — 專為中文醫療文本設計，支援簡繁體中文

## 🚀 快速開始

### 安裝

```bash
git clone https://github.com/gitstq/MedTextCN-Plus.git
cd MedTextCN-Plus
pip install -e .
pip install -e ".[all]"  # 全部功能
```

### 基礎使用

```python
from medtextcn_plus import MedTextAnalyzer

analyzer = MedTextAnalyzer()

text = "患者張三，男，45歲，因反覆咳嗽、發熱3天入院。既往有高血壓病史，長期服用氨氯地平。"

# NER實體識別
entities = analyzer.extract_entities(text)
for ent in entities:
    print(f"[{ent.entity_type}] {ent.text}")

# PII隱私脫敏
sanitized = analyzer.sanitize_pii(text)
print(f"脫敏結果: {sanitized}")

# 智慧摘要
summary = analyzer.summarize(text, max_length=50)
print(f"摘要: {summary}")

# 藥物交互檢測
interactions = analyzer.detect_drug_interactions(["阿莫西林", "布洛芬", "氨氯地平"])
for i in interactions:
    print(f"[{i.severity}] {i.drug_a} + {i.drug_b}: {i.description}")
```

### 命令列使用

```bash
medtext analyze --input medical_report.txt --output results.json
medtext sanitize --input patient_data.txt --output sanitized.txt
medtext serve --host 0.0.0.0 --port 8080
medtext tui
```

## 📖 詳細使用指南

### NER實體識別

支援8大類醫療實體：DISEASE（疾病）、SYMPTOM（症狀）、DRUG（藥物）、TEST（檢查項目）、BODY_PART（身體部位）、TREATMENT（治療方案）、TIME（時間表達）、LAB_VALUE（檢驗數值）。

### PII隱私脫敏

自動識別並脫敏：患者姓名、身分證號、手機號、住址、醫保卡號、就診卡號、電子郵箱、出生日期、職業。

### REST API

```bash
curl -X POST http://localhost:8080/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "患者因反覆咳嗽入院...", "options": {"ner": true, "pii": true, "summary": true}}'
```

## 📦 打包與部署

```bash
python -m build
docker build -t medtextcn-plus .
docker run -p 8080:8080 medtextcn-plus
```

## 🤝 貢獻指南

歡迎貢獻代碼！請遵循 [Conventional Commits](https://www.conventionalcommits.org/) 提交規範。

## 📄 開源協議

本项目基於 [MIT License](LICENSE) 開源。

---

**⚠️ 免責聲明**：本工具僅供學術研究和技术學習使用，不構成任何醫療建議或診斷依據。
