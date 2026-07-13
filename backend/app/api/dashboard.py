from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.responses import ok
from app.core.security import get_current_user
from app.database.session import get_db
from app.models import AgentTask, CottonField, Recommendation, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def task_brief(task: AgentTask) -> dict:
    return {
        "id": task.id,
        "fieldId": task.fieldId,
        "fieldName": task.field.name if task.field else "",
        "status": task.status,
        "riskLevel": task.riskLevel,
        "decision": task.decision,
        "description": task.description,
        "createdAt": task.createdAt,
    }


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
    return ok([{"date": str(day), "count": sum(1 for task in tasks if task.createdAt.date() == day)} for day in days])


@router.get("/action-distribution")
def action_distribution(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.execute(
        select(Recommendation.actionName, func.count())
        .join(AgentTask)
        .where(AgentTask.userId == user.id)
        .group_by(Recommendation.actionName)
    ).all()
    return ok([{"name": name, "value": count} for name, count in rows])


@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = dict(db.execute(
        select(AgentTask.riskLevel, func.count())
        .where(AgentTask.userId == user.id)
        .group_by(AgentTask.riskLevel)
    ).all())
    labels = {"low": "低风险", "medium": "中风险", "high": "高风险"}
    return ok([{"name": labels[level], "code": level, "value": rows.get(level, 0)} for level in ["low", "medium", "high"]])


@router.get("/growth-stage-distribution")
def growth_stage_distribution(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = dict(db.execute(
        select(CottonField.growthStage, func.count())
        .where(CottonField.userId == user.id)
        .group_by(CottonField.growthStage)
    ).all())
    stages = ["播种期", "苗期", "蕾期", "花铃期", "吐絮期"]
    return ok([{"name": stage, "value": rows.get(stage, 0)} for stage in stages])


@router.get("/decision-distribution")
def decision_distribution(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = dict(db.execute(
        select(AgentTask.decision, func.count())
        .where(AgentTask.userId == user.id)
        .group_by(AgentTask.decision)
    ).all())
    labels = {"accepted": "已接受", "rejected": "已拒绝", "pending": "待确认"}
    return ok([{"name": labels[decision], "code": decision, "value": rows.get(decision, 0)} for decision in ["accepted", "rejected", "pending"]])


@router.get("/pending-tasks")
def pending_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pending = db.scalars(
        select(AgentTask)
        .where(AgentTask.userId == user.id, AgentTask.status == "success", AgentTask.decision == "pending")
        .order_by(AgentTask.createdAt.desc())
        .limit(5)
    ).all()
    risky = db.scalars(
        select(AgentTask)
        .where(AgentTask.userId == user.id, AgentTask.riskLevel.in_(["medium", "high"]))
        .order_by(AgentTask.createdAt.desc())
        .limit(5)
    ).all()
    return ok({"pendingDecisionTasks": [task_brief(task) for task in pending], "mediumHighRiskTasks": [task_brief(task) for task in risky]})


@router.get("/abnormal-fields")
def abnormal_fields(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    fields = db.scalars(select(CottonField).where(CottonField.userId == user.id)).all()
    results = []
    for field in fields:
        latest = db.scalar(
            select(AgentTask)
            .where(AgentTask.userId == user.id, AgentTask.fieldId == field.id)
            .order_by(AgentTask.createdAt.desc())
            .limit(1)
        )
        if latest and latest.riskLevel in {"medium", "high"}:
            results.append({
                "fieldId": field.id,
                "fieldName": field.name,
                "region": field.region,
                "growthStage": field.growthStage,
                "riskLevel": latest.riskLevel,
                "taskId": latest.id,
                "taskCreatedAt": latest.createdAt,
                "description": latest.description,
            })
    return ok(results[:5])


@router.get("/recent-tasks")
def recent_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tasks = db.scalars(select(AgentTask).where(AgentTask.userId == user.id).order_by(AgentTask.createdAt.desc()).limit(5)).all()
    return ok([task_brief(task) for task in tasks])
