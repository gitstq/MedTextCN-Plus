# MedTextCN-Plus: Chinese Medical Text Intelligence Engine Pro

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/Code%20Style-Black-black.svg)](https://github.com/psf/black)

> A lightweight Chinese medical text intelligence engine — NER Entity Recognition | PII Privacy Sanitization | Intelligent Summarization | Relation Extraction | Drug Interaction Detection | Zero Core Dependencies

## 🎉 Introduction

MedTextCN-Plus is a lightweight text intelligence analysis engine designed specifically for Chinese medical scenarios. It provides a complete toolchain from basic text processing to advanced medical AI analysis, supporting offline operation, patient privacy protection, and is suitable for medical informatics, clinical research, and health technology.

Unlike general-purpose medical AI tools, MedTextCN-Plus deeply optimizes for the unique requirements of Chinese medical texts: Chinese word segmentation, medical entity recognition, patient privacy information sanitization, and drug interaction detection.

## ✨ Core Features

- **🩺 Medical NER** — Recognize 8 major medical entity types: diseases, symptoms, drugs, tests, body parts, treatments, time expressions, lab values
- **🔒 PII Sanitization** — Auto-detect and sanitize patient names, ID cards, phone numbers, addresses, and other sensitive information
- **📝 Text Summarization** — Extractive Chinese medical text auto-summarization
- **🔗 Relation Extraction** — Identify drug-disease, symptom-disease, drug-symptom entity relationships
- **💊 Drug Interaction Detection** — Detect potential drug interactions and contraindications
- **📊 Multi-dimensional Analysis** — Sentiment analysis, keyword extraction, text classification, similarity computation
- **🧠 Multi-model Backend** — Support rule engine, TF-IDF, Word2Vec, BERT analysis backends
- **🖥️ Interactive TUI** — Beautiful terminal interface with real-time analysis
- **🌐 REST API** — Built-in HTTP server for remote invocation
- **📦 Zero Core Dependencies** — Pure Python core, optional dependencies install on demand
- **🇨🇳 Chinese-Optimized** — Designed for Chinese medical texts, supports Simplified & Traditional Chinese

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/gitstq/MedTextCN-Plus.git
cd MedTextCN-Plus
pip install -e .
pip install -e ".[all]"  # All features
```

### Basic Usage

```python
from medtextcn_plus import MedTextAnalyzer

analyzer = MedTextAnalyzer()

text = "Patient Zhang San, male, 45 years old, admitted for recurrent cough and fever for 3 days. History of hypertension, long-term use of amlodipine."

# NER Entity Recognition
entities = analyzer.extract_entities(text)
for ent in entities:
    print(f"[{ent.entity_type}] {ent.text} (confidence: {ent.confidence:.2f})")

# PII Privacy Sanitization
sanitized = analyzer.sanitize_pii(text)
print(f"Sanitized: {sanitized}")

# Intelligent Summarization
summary = analyzer.summarize(text, max_length=50)
print(f"Summary: {summary}")

# Drug Interaction Detection
interactions = analyzer.detect_drug_interactions(["amoxicillin", "ibuprofen", "amlodipine"])
for i in interactions:
    print(f"[{i.severity}] {i.drug_a} + {i.drug_b}: {i.description}")
```

### CLI Usage

```bash
medtext analyze --input medical_report.txt --output results.json
medtext sanitize --input patient_data.txt --output sanitized.txt
medtext serve --host 0.0.0.0 --port 8080
medtext tui
```

## 📖 Detailed Guide

### NER Entity Types

| Type | Description | Examples |
|------|-------------|----------|
| DISEASE | Disease names | Hypertension, Diabetes, URI |
| SYMPTOM | Symptoms | Cough, Fever, Headache |
| DRUG | Drug names | Amoxicillin, Ibuprofen |
| TEST | Test items | Blood routine, CT, MRI |
| BODY_PART | Body parts | Lungs, Liver, Heart |
| TREATMENT | Treatments | Surgery, Chemotherapy |
| TIME | Time expressions | 3 days, 2 weeks |
| LAB_VALUE | Lab values | 38.5°C, 145/90mmHg |

### REST API

```bash
curl -X POST http://localhost:8080/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient admitted for cough...", "options": {"ner": true, "pii": true, "summary": true}}'
```

## 📦 Build & Deploy

```bash
python -m build
docker build -t medtextcn-plus .
docker run -p 8080:8080 medtextcn-plus
```

## 🤝 Contributing

Contributions are welcome! Please follow [Conventional Commits](https://www.conventionalcommits.org/).

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

**⚠️ Disclaimer**: This tool is for academic research and technical learning only. It does not constitute any medical advice or diagnostic basis.
