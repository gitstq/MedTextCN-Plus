FROM python:3.11-slim

LABEL maintainer="MedTextCN-Plus Contributors"
LABEL description="中文医疗文本智能分析引擎 Pro"

WORKDIR /app

COPY pyproject.toml .
COPY medtextcn_plus/ medtextcn_plus/

RUN pip install --no-cache-dir -e ".[all]" && \
    rm -rf /root/.cache/pip

EXPOSE 8080

CMD ["medtext", "serve", "--host", "0.0.0.0", "--port", "8080"]
