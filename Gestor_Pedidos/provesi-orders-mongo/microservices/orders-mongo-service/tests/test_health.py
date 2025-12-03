from fastapi.testclient import TestClient
from microservices.orders-mongo-service.app.main import app  # puede requerir ajustar el import según tu PYTHONPATH

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
