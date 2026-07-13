import asyncio
from datetime import date, datetime, time

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.responses import ok
from app.core.security import get_current_user
from app.database.session import SessionLocal, get_db
from app.models import AgentTask, User
from app.schemas.agent import AgentTaskCreate
from app.services.agent_task_service import AgentTaskService, task_to_detail
from app.services.task_event_broker import broker, sse_format

router = APIRouter(prefix="/agent", tags=["agent"])
service = AgentTaskService(SessionLocal)


@router.post("/tasks")
def create_task(payload: AgentTaskCreate, background: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        task = service.create_task(db, user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    background.add_task(service.run_task, task.id)
    return ok({"taskId": task.id, "status": "running"})


@router.get("/tasks")
def list_tasks(
    status: str = "",
    fieldId: int | None = None,
    riskLevel: str = "",
    decision: str = "",
    keyword: str = "",
    dateFrom: date | None = None,
    dateTo: date | None = None,
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page = max(page, 1)
    pageSize = min(max(pageSize, 1), 100)
    stmt = select(AgentTask).where(AgentTask.userId == user.id).order_by(AgentTask.createdAt.desc())
    if status:
        stmt = stmt.where(AgentTask.status == status)
    if fieldId:
        stmt = stmt.where(AgentTask.fieldId == fieldId)
    if riskLevel:
        stmt = stmt.where(AgentTask.riskLevel == riskLevel)
    if decision:
        stmt = stmt.where(AgentTask.decision == decision)
    if keyword:
        stmt = stmt.where(AgentTask.description.contains(keyword))
    if dateFrom:
        stmt = stmt.where(AgentTask.createdAt >= datetime.combine(dateFrom, time.min))
    if dateTo:
        stmt = stmt.where(AgentTask.createdAt <= datetime.combine(dateTo, time.max))

    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    tasks = db.scalars(stmt.offset((page - 1) * pageSize).limit(pageSize)).all()
    return ok({"items": [task_to_detail(t) for t in tasks], "total": total, "page": page, "pageSize": pageSize})


@router.get("/tasks/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.scalar(select(AgentTask).where(AgentTask.id == task_id, AgentTask.userId == user.id))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return ok(task_to_detail(task))


@router.get("/tasks/{task_id}/events")
async def task_events(task_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.scalar(select(AgentTask).where(AgentTask.id == task_id, AgentTask.userId == user.id))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    async def stream():
        queue = broker.subscribe(task_id)
        try:
            snapshot_db = SessionLocal()
            snapshot = snapshot_db.scalar(select(AgentTask).where(AgentTask.id == task_id))
            yield sse_format(broker.make_event("task_snapshot", task_id, task_to_detail(snapshot)))
            snapshot_db.close()
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    event = broker.make_event("heartbeat", task_id, {})
                yield sse_format(event)
                if event["type"] in {"completed", "failed"}:
                    break
        finally:
            broker.unsubscribe(task_id, queue)

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/tasks/{task_id}/accept")
def accept_task(task_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.scalar(select(AgentTask).where(AgentTask.id == task_id, AgentTask.userId == user.id))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    task.decision = "accepted"
    db.commit()
    return ok(True)


@router.post("/tasks/{task_id}/reject")
def reject_task(task_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.scalar(select(AgentTask).where(AgentTask.id == task_id, AgentTask.userId == user.id))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    task.decision = "rejected"
    db.commit()
    return ok(True)
