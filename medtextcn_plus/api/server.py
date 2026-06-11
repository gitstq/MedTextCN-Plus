"""REST API 服务"""

import json
from typing import Dict, Any, Optional

try:
    from flask import Flask, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


def create_app() -> "Flask":
    """创建Flask应用"""
    if not HAS_FLASK:
        raise ImportError(
            "Flask is required for the API server. "
            "Install it with: pip install medtextcn-plus[server]"
        )

    from medtextcn_plus.core.engine import MedTextAnalyzer

    app = Flask(__name__)
    analyzer = MedTextAnalyzer()

    @app.route("/health", methods=["GET"])
    def health():
        """健康检查"""
        return jsonify({"status": "ok", "version": "1.2.0"})

    @app.route("/api/v1/analyze", methods=["POST"])
    def analyze():
        """综合分析接口"""
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        options = data.get("options", {})
        result = analyzer.analyze(text, options)
        return jsonify(result)

    @app.route("/api/v1/ner", methods=["POST"])
    def ner():
        """NER实体识别接口"""
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        entities = analyzer.extract_entities(data["text"])
        return jsonify({
            "entities": [e.to_dict() for e in entities],
            "count": len(entities),
        })

    @app.route("/api/v1/pii/detect", methods=["POST"])
    def pii_detect():
        """PII检测接口"""
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        matches = analyzer.detect_pii(data["text"])
        return jsonify({
            "pii_matches": [m.to_dict() for m in matches],
            "count": len(matches),
        })

    @app.route("/api/v1/pii/sanitize", methods=["POST"])
    def pii_sanitize():
        """PII脱敏接口"""
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        result = analyzer.sanitize_pii_full(data["text"])
        return jsonify(result.to_dict())

    @app.route("/api/v1/summary", methods=["POST"])
    def summary():
        """文本摘要接口"""
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        result = analyzer.summarize(
            data["text"],
            max_length=data.get("max_length", 100),
            sentence_count=data.get("sentence_count", 3),
            method=data.get("method", "combined"),
        )
        return jsonify({"summary": result})

    @app.route("/api/v1/relations", methods=["POST"])
    def relations():
        """关系抽取接口"""
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        relations = analyzer.extract_relations(data["text"])
        return jsonify({
            "relations": [r.to_dict() for r in relations],
            "count": len(relations),
        })

    @app.route("/api/v1/drug-interactions", methods=["POST"])
    def drug_interactions():
        """药物交互检测接口"""
        data = request.get_json()
        if not data or "drugs" not in data:
            return jsonify({"error": "Missing 'drugs' field"}), 400

        interactions = analyzer.detect_drug_interactions(data["drugs"])
        return jsonify({
            "interactions": [i.to_dict() for i in interactions],
            "count": len(interactions),
        })

    @app.route("/api/v1/keywords", methods=["POST"])
    def keywords():
        """关键词提取接口"""
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        kws = analyzer.extract_keywords(data["text"], top_n=data.get("top_n", 10))
        return jsonify({
            "keywords": [{"word": w, "score": s} for w, s in kws],
        })

    @app.route("/api/v1/sentiment", methods=["POST"])
    def sentiment():
        """情感分析接口"""
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        result = analyzer.analyze_sentiment(data["text"])
        return jsonify(result)

    return app
