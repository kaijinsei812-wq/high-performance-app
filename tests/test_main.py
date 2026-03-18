import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///./test_temp.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # slowapiのレート制限ストレージをリセット
    from app.limiter import limiter
    limiter._storage_uri = "memory://"
    try:
        limiter._storage.reset()
    except Exception:
        pass
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def get_auth_headers(username="testuser", password="testpass123"):
    client.post("/api/v1/auth/register", json={
        "email": f"{username}@example.com",
        "username": username,
        "password": password,
    })
    res = client.post("/api/v1/auth/token", data={
        "username": username,
        "password": password,
    })
    token = res.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_register():
    res = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    })
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"


def test_register_duplicate():
    client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    })
    res = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser2",
        "password": "testpass123",
    })
    assert res.status_code == 400


def test_login():
    headers = get_auth_headers()
    assert "Bearer " in headers["Authorization"]


def test_login_wrong_password():
    client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    })
    res = client.post("/api/v1/auth/token", data={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert res.status_code == 401


def test_me_endpoint():
    headers = get_auth_headers()
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"


def test_create_item():
    headers = get_auth_headers()
    res = client.post("/api/v1/items/", json={
        "name": "テストアイテム",
        "description": "説明",
        "price": 1000.0,
    }, headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "テストアイテム"


def test_list_items():
    headers = get_auth_headers()
    client.post("/api/v1/items/", json={"name": "A", "price": 100.0}, headers=headers)
    client.post("/api/v1/items/", json={"name": "B", "price": 200.0}, headers=headers)
    res = client.get("/api/v1/items/")
    assert res.status_code == 200
    assert len(res.json()) >= 2


def test_update_item():
    headers = get_auth_headers()
    create_res = client.post("/api/v1/items/", json={"name": "旧名前", "price": 100.0}, headers=headers)
    assert create_res.status_code == 200
    item_id = create_res.json()["id"]
    res = client.put(f"/api/v1/items/{item_id}", json={"name": "新名前", "price": 200.0}, headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "新名前"


def test_delete_item():
    headers = get_auth_headers()
    create_res = client.post("/api/v1/items/", json={"name": "削除テスト", "price": 100.0}, headers=headers)
    assert create_res.status_code == 200
    item_id = create_res.json()["id"]
    res = client.delete(f"/api/v1/items/{item_id}", headers=headers)
    assert res.status_code == 200


def test_item_not_found():
    res = client.get("/api/v1/items/99999")
    assert res.status_code == 404


def test_create_item_unauthenticated():
    res = client.post("/api/v1/items/", json={"name": "test", "price": 100.0})
    assert res.status_code == 401
