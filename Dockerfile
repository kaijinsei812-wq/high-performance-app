# ─── ビルドステージ ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─── 本番ステージ ─────────────────────────────────────────────────
FROM python:3.11-slim AS production

# セキュリティ: 非rootユーザー
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# 依存パッケージのみコピー
COPY --from=builder /install /usr/local

# アプリコードをコピー
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# 起動スクリプト（マイグレーション → サーバー起動）
COPY scripts/start.sh ./scripts/start.sh
RUN chmod +x ./scripts/start.sh && chown -R appuser:appuser /app

USER appuser

ENV PORT=8000
EXPOSE $PORT

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen(f'http://localhost:{__import__(\"os\").getenv(\"PORT\",\"8000\")}/health')" || exit 1

CMD ["./scripts/start.sh"]
