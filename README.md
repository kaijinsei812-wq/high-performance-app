# High Performance App 🚀

高性能APIサーバー - FastAPI / Python / PostgreSQL

## 🛠 技術スタック
- **FastAPI** - 高性能Webフレームワーク
- **PostgreSQL** - データベース
- **SQLAlchemy** - ORM
- **Docker** - コンテナ化
- **Pydantic** - データバリデーション

## 🚀 クイックスタート

```bash
# 依存関係インストール
pip install -r requirements.txt

# 開発サーバー起動
uvicorn app.main:app --reload

# Dockerで起動
docker-compose up
```

## 📚 API ドキュメント
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 テスト
```bash
pytest tests/
```
