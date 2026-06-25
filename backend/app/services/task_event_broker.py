import asyncio
import json
import time
from collections import defaultdict


class TaskEventBroker:
    def __init__(self):
        self.subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)

    def make_event(self, event_type: str, task_id: str, data: dict | list | None = None) -> dict:
        return {"type": event_type, "taskId": task_id, "timestamp": int(time.time() * 1000), "data": data or {}}

    async def publish(self, task_id: str, event: dict) -> None:
        for queue in list(self.subscribers.get(task_id, [])):
            await queue.put(event)

    def subscribe(self, task_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.subscribers[task_id].append(queue)
        return queue

    def unsubscribe(self, task_id: str, queue: asyncio.Queue) -> None:
        if task_id in self.subscribers and queue in self.subscribers[task_id]:
            self.subscribers[task_id].remove(queue)


broker = TaskEventBroker()


def sse_format(event: dict) -> str:
    return f"event: {event['type']}\ndata: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"
