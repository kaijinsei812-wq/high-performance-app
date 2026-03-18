#!/bin/bash
set -e

echo "🔄 DBマイグレーション実行中..."
alembic upgrade head

echo "🚀 サーバー起動..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
