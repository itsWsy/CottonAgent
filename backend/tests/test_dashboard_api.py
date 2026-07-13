from fastapi.testclient import TestClient

from app.database.init_db import init_db
from app.main import app


def auth_headers(client: TestClient) -> dict:
    token = client.post("/api/auth/login", json={"username": "admin", "password": "123456"}).json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_endpoints_return_success():
    init_db()
    client = TestClient(app)
    headers = auth_headers(client)
    for path in [
        "/api/dashboard/summary",
        "/api/dashboard/task-trend",
        "/api/dashboard/action-distribution",
        "/api/dashboard/risk-distribution",
        "/api/dashboard/growth-stage-distribution",
        "/api/dashboard/decision-distribution",
        "/api/dashboard/pending-tasks",
        "/api/dashboard/abnormal-fields",
        "/api/dashboard/recent-tasks",
    ]:
        response = client.get(path, headers=headers)
        assert response.status_code == 200
        assert response.json()["code"] == 0
