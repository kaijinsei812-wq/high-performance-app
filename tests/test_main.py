from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_create_item():
    res = client.post("/api/v1/items", json={"name": "テストアイテム", "description": "説明", "price": 100.0})
    assert res.status_code == 200
    assert res.json()["name"] == "テストアイテム"

def test_get_items():
    res = client.get("/api/v1/items")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
