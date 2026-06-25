from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.responses import ok
from app.core.security import get_current_user
from app.database.session import get_db
from app.models import AgentTask, CottonField, Recommendation, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    week_start = datetime.utcnow() - timedelta(days=7)
    return ok({
        "fieldCount": db.scalar(select(func.count()).select_from(CottonField).where(CottonField.userId == user.id)),
        "weeklyTaskCount": db.scalar(select(func.count()).select_from(AgentTask).where(AgentTask.userId == user.id, AgentTask.createdAt >= week_start)),
        "pendingDecisionCount": db.scalar(select(func.count()).select_from(AgentTask).where(AgentTask.userId == user.id, AgentTask.decision == "pending", AgentTask.status == "success")),
        "mediumHighRiskCount": db.scalar(select(func.count()).select_from(AgentTask).where(AgentTask.userId == user.id, AgentTask.riskLevel.in_(["medium", "high"]))),
    })


@router.get("/task-trend")
def task_trend(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    days = [(datetime.utcnow() - timedelta(days=i)).date() for i in range(6, -1, -1)]
    tasks = db.scalars(select(AgentTask).where(AgentTask.userId == user.id)).all()
    return ok([{"date": str(day), "count": sum(1 for t in tasks if t.createdAt.date() == day)} for day in days])


@router.get("/action-distribution")
def action_distribution(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.execute(select(Recommendation.actionName, func.count()).join(AgentTask).where(AgentTask.userId == user.id).group_by(Recommendation.actionName)).all()
    return ok([{"name": name, "value": count} for name, count in rows])


@router.get("/recent-tasks")
def recent_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tasks = db.scalars(select(AgentTask).where(AgentTask.userId == user.id).order_by(AgentTask.createdAt.desc()).limit(5)).all()
    return ok([{"id": t.id, "fieldName": t.field.name if t.field else "", "status": t.status, "riskLevel": t.riskLevel, "decision": t.decision, "description": t.description, "createdAt": t.createdAt} for t in tasks])
