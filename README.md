# 🚀 High Performance App

FastAPI + PostgreSQL + Redis + Celery + Prometheus による本番級APIサーバー

## スタック

| カテゴリ | 技術 |
|---------|------|
| API | FastAPI 0.110 |
| DB | PostgreSQL + SQLAlchemy + Alembic |
| キャッシュ | Redis |
| 認証 | JWT (access 15分 + refresh 7日) |
| レート制限 | slowapi |
| 非同期処理 | Celery + Redis |
| 監視 | Prometheus + Grafana |
| コンテナ | Docker (multi-stage) |
| CI/CD | GitHub Actions |

## ローカル起動

```bash
# 全サービス起動（DB / Redis / Prometheus / Grafana 含む）
docker-compose up -d

# API:        http://localhost:8000
# API Docs:   http://localhost:8000/docs
# Metrics:    http://localhost:8000/metrics
# Grafana:    http://localhost:3000  (admin / admin)
# Prometheus: http://localhost:9090
```

## Renderへのデプロイ

```bash
# 1. GitHubにpush済みであることを確認
# 2. https://render.com でアカウント作成
# 3. New → Blueprint → GitHubリポジトリを選択
# 4. render.yaml が自動検出されてデプロイ完了
```

## 主要エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| GET | /health | ヘルスチェック |
| POST | /api/v1/auth/register | ユーザー登録 |
| POST | /api/v1/auth/token | ログイン (access + refresh token) |
| POST | /api/v1/auth/refresh | トークンリフレッシュ |
| POST | /api/v1/auth/logout | ログアウト |
| GET | /api/v1/auth/me | 現在のユーザー情報 |
| GET | /api/v1/items/ | アイテム一覧 (Redisキャッシュ) |
| POST | /api/v1/items/ | アイテム作成 |
| POST | /api/v1/items/{id}/process | 非同期処理キュー追加 |
| GET | /api/v1/items/tasks/{task_id} | Celeryタスク状態確認 |
| GET | /metrics | Prometheusメトリクス |

## テスト

```bash
pip install -r requirements.txt
DATABASE_URL=sqlite:///./test.db SECRET_KEY=test-secret pytest tests/ -v
```

## 環境変数

`.env.example` を参照。
