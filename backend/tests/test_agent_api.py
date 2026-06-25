import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.gettempdir()}/cotton_pilot_test.db"
os.environ["AGENT_STEP_DELAY_MS"] = "0"

from fastapi.testclient import TestClient

from app.database.init_db import init_db
from app.main import app


def test_create_agent_task():
    init_db()
    client = TestClient(app)
    token = client.post("/api/auth/login", json={"username": "admin", "password": "123456"}).json()["data"]["token"]
    fields = client.get("/api/fields", headers={"Authorization": f"Bearer {token}"}).json()["data"]
    resp = client.post(
        "/api/agent/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"fieldId": fields[0]["id"], "growthStage": "花铃期", "symptoms": ["叶片卷曲", "发现蚜虫"], "weatherTags": ["高温", "少雨"], "description": "如何安排下一步观察？"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "running"
