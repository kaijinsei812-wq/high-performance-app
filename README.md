# High Performance App 🚀

高性能APIサーバー - FastAPI / Python / PostgreSQL / JWT認証 / Docker

## 🛠 技術スタック
- **FastAPI** - 高性能Webフレームワーク
- **PostgreSQL** - データベース (開発時はSQLite)
- **SQLAlchemy** - ORM
- **JWT (jose)** - 認証
- **bcrypt (passlib)** - パスワードハッシュ
- **Docker / docker-compose** - コンテナ化
- **pytest** - テスト自動化

## 🚀 クイックスタート

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📚 API ドキュメント
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔑 認証フロー
1. `POST /api/v1/auth/register` でユーザー登録
2. `POST /api/v1/auth/token` でJWTトークン取得
3. `Authorization: Bearer <token>` ヘッダーでAPI利用

## 🧪 テスト
```bash
pytest tests/ -v
```

## 🐳 Docker
```bash
docker-compose up
```
