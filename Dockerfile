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

# 所有権変更
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
