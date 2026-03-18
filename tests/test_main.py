from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_register_and_login():
    # Register
    res = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    })
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"

    # Login
    res = client.post("/api/v1/auth/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_create_item_authenticated():
    # Login first
    res = client.post("/api/v1/auth/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    token = res.json().get("access_token", "")
    headers = {"Authorization": f"Bearer {token}"}

    # Create item
    res = client.post("/api/v1/items/", json={
        "name": "テストアイテム",
        "description": "説明",
        "price": 1000.0
    }, headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "テストアイテム"
