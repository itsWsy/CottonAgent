import json
from datetime import datetime

from app.services.task_event_broker import sse_format


def test_sse_format_serializes_datetime_snapshot():
    text = sse_format({"type": "task_snapshot", "taskId": "t1", "timestamp": 1, "data": {"createdAt": datetime(2026, 6, 23, 12, 0)}})
    payload = json.loads(text.split("data: ", 1)[1])
    assert payload["data"]["createdAt"] == "2026-06-23 12:00:00"
