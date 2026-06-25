import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Callable

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.core.config import settings
from app.models import AgentStep, AgentTask, CottonField, FarmRecord, Recommendation
from app.schemas.agent import AgentTaskCreate
from app.services.knowledge_service import KnowledgeService
from app.services.llm_service import LLMService
from app.services.recommendation_service import RecommendationService
from app.services.task_event_broker import broker

STEPS = [
    ("validate_input", "校验咨询信息"),
    ("load_field_context", "读取棉田档案"),
    ("load_history_records", "获取历史农事记录"),
    ("retrieve_knowledge", "检索棉花领域知识"),
    ("recommend_next_actions", "推荐下一步农事操作"),
    ("generate_farm_plan", "生成 7 天农事计划"),
    ("generate_final_answer", "生成最终说明"),
    ("save_task_result", "保存任务结果"),
]


def dumps(data) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


def loads(text: str, default):
    try:
        return json.loads(text) if text else default
    except json.JSONDecodeError:
        return default


def risk_level(symptoms: list[str]) -> str:
    if "发现棉铃虫" in symptoms and "落蕾" in symptoms:
        return "high"
    if "发现蚜虫" in symptoms and "叶片卷曲" in symptoms:
        return "medium"
    if len(symptoms) >= 3:
        return "medium"
    return "low"


def risk_reason(symptoms: list[str]) -> str:
    if "发现棉铃虫" in symptoms and "落蕾" in symptoms:
        return "同时出现“发现棉铃虫”和“落蕾”，触发高风险规则。"
    if "发现蚜虫" in symptoms and "叶片卷曲" in symptoms:
        return "同时出现“发现蚜虫”和“叶片卷曲”，触发中风险规则。"
    if len(symptoms) >= 3:
        return "症状数量达到 3 个或以上，触发中风险规则。"
    return "未触发中高风险规则，暂按低风险展示。"


def task_to_detail(task: AgentTask) -> dict:
    return {
        "id": task.id,
        "fieldId": task.fieldId,
        "fieldName": task.field.name if task.field else None,
        "description": task.description,
        "growthStage": task.growthStage,
        "symptoms": loads(task.symptoms, []),
        "weatherTags": loads(task.weatherTags, []),
        "riskLevel": task.riskLevel,
        "riskReason": risk_reason(loads(task.symptoms, [])),
        "status": task.status,
        "decision": task.decision,
        "farmPlan": loads(task.farmPlan, []),
        "evidences": loads(task.evidences, []),
        "finalAnswer": task.finalAnswer,
        "errorMessage": task.errorMessage,
        "createdAt": task.createdAt,
        "completedAt": task.completedAt,
        "steps": [step_to_out(s) for s in sorted(task.steps, key=lambda x: x.id)],
        "recommendations": [rec_to_out(r) for r in task.recommendations],
    }


def step_summary(step_id: str, output: dict | list | str | None) -> str:
    if step_id == "validate_input":
        return "咨询信息已通过校验。"
    if step_id == "load_field_context" and isinstance(output, dict):
        return f"已读取“{output.get('name', '棉田')}”档案。"
    if step_id == "load_history_records" and isinstance(output, dict):
        return f"已获取 {len(output.get('records', []))} 条历史农事记录。"
    if step_id == "retrieve_knowledge" and isinstance(output, dict):
        return f"已检索到 {len(output.get('items', []))} 条相关知识。"
    if step_id == "recommend_next_actions" and isinstance(output, dict):
        return f"已生成 {len(output.get('recommendations', []))} 条推荐操作。"
    if step_id == "generate_farm_plan" and isinstance(output, dict):
        return f"已生成 {len(output.get('farmPlan', []))} 个 7 天计划项。"
    if step_id == "generate_final_answer":
        return "最终说明已生成。"
    if step_id == "save_task_result":
        return "任务结果已保存，可刷新恢复。"
    return "步骤已完成。"


def step_to_out(step: AgentStep) -> dict:
    output = loads(step.outputData, {})
    return {
        "stepId": step.stepId,
        "name": step.stepName,
        "status": step.status,
        "startTime": step.createdAt,
        "endTime": step.updatedAt,
        "duration": step.duration,
        "input": loads(step.inputData, {}),
        "output": output,
        "summary": step_summary(step.stepId, output) if step.status == "success" else "",
        "errorMessage": step.errorMessage,
    }


def rec_to_out(rec: Recommendation) -> dict:
    return {
        "actionCode": rec.actionCode,
        "actionName": rec.actionName,
        "score": rec.score,
        "scoreBreakdown": loads(rec.scoreBreakdown, {}),
        "expectedDay": rec.expectedDay,
        "reason": rec.reason,
        "reasonItems": loads(rec.reasonItems, []),
        "sourceType": rec.sourceType,
    }


def recommendation_model_kwargs(task_id: str, item: dict) -> dict:
    return {
        "taskId": task_id,
        "actionCode": item["actionCode"],
        "actionName": item["actionName"],
        "score": item["score"],
        "reason": item["reason"],
        "scoreBreakdown": dumps(item.get("scoreBreakdown", {})),
        "reasonItems": dumps(item.get("reasonItems", [])),
        "expectedDay": item["expectedDay"],
        "sourceType": item["sourceType"],
    }


class AgentTaskService:
    def __init__(self, db_factory: Callable[[], Session]):
        self.db_factory = db_factory
        self.knowledge = KnowledgeService()
        self.recommender = RecommendationService()
        self.llm = LLMService()

    def create_task(self, db: Session, user_id: int, payload: AgentTaskCreate) -> AgentTask:
        field = db.scalar(select(CottonField).where(CottonField.id == payload.fieldId, CottonField.userId == user_id))
        if not field:
            raise ValueError("棉田不存在")
        task = AgentTask(
            id=str(uuid.uuid4()),
            userId=user_id,
            fieldId=payload.fieldId,
            description=payload.description,
            growthStage=payload.growthStage,
            symptoms=dumps(payload.symptoms),
            weatherTags=dumps(payload.weatherTags),
            riskLevel=risk_level(payload.symptoms),
            status="running",
        )
        db.add(task)
        db.flush()
        for step_id, step_name in STEPS:
            db.add(AgentStep(taskId=task.id, stepId=step_id, stepName=step_name, status="waiting"))
        db.commit()
        db.refresh(task)
        return task

    async def run_task(self, task_id: str) -> None:
        db = self.db_factory()
        try:
            task = db.get(AgentTask, task_id)
            state = AgentState(
                taskId=task.id,
                userId=task.userId,
                fieldId=task.fieldId,
                description=task.description,
                growthStage=task.growthStage,
                symptoms=loads(task.symptoms, []),
                weatherTags=loads(task.weatherTags, []),
                riskLevel=task.riskLevel,
            )
            await self._run_step(db, state, "validate_input", {"description": state.description}, lambda: self._validate(state))
            await self._run_step(db, state, "load_field_context", {"fieldId": state.fieldId}, lambda: self._load_field(db, state))
            await self._run_step(db, state, "load_history_records", {"fieldId": state.fieldId}, lambda: self._load_records(db, state))
            await self._run_step(db, state, "retrieve_knowledge", {"symptoms": state.symptoms, "weatherTags": state.weatherTags}, lambda: self._retrieve(state))
            await self._run_step(db, state, "recommend_next_actions", {}, lambda: self._recommend(state))
            await self._publish_and_store(db, state, "recommendations", state.recommendations)
            await self._run_step(db, state, "generate_farm_plan", {}, lambda: self._plan(state))
            await self._publish_and_store(db, state, "farm_plan", state.farmPlan)
            await self._publish_and_store(db, state, "evidences", state.knowledgeItems)
            await self._run_step_async(db, state, "generate_final_answer", {}, lambda: self.llm.generate_answer(state.__dict__))
            await self._publish_and_store(db, state, "answer", {"answer": state.finalAnswer})
            await self._run_step(db, state, "save_task_result", {}, lambda: self._save_final(db, state))
            task = db.get(AgentTask, task_id)
            task.status = "success"
            task.completedAt = datetime.utcnow()
            db.commit()
            await broker.publish(task_id, broker.make_event("completed", task_id, task_to_detail(task)))
        except Exception as exc:
            task = db.get(AgentTask, task_id)
            if task:
                task.status = "failed"
                task.errorMessage = str(exc)
                task.completedAt = datetime.utcnow()
                db.commit()
            await broker.publish(task_id, broker.make_event("failed", task_id, {"errorMessage": str(exc)}))
        finally:
            db.close()

    async def _run_step(self, db, state, step_id, input_data, func):
        return await self._run_step_async(db, state, step_id, input_data, lambda: asyncio.to_thread(func))

    async def _run_step_async(self, db, state, step_id, input_data, func):
        step = db.scalar(select(AgentStep).where(AgentStep.taskId == state.taskId, AgentStep.stepId == step_id))
        step.status = "running"
        step.inputData = dumps(input_data)
        step.updatedAt = datetime.utcnow()
        db.commit()
        await broker.publish(state.taskId, broker.make_event("step_start", state.taskId, {"stepId": step.stepId, "stepName": step.stepName}))
        start = time.perf_counter()
        try:
            if settings.agent_step_delay_ms:
                await asyncio.sleep(settings.agent_step_delay_ms / 1000)
            output = await func()
            if step_id == "generate_final_answer":
                state.finalAnswer = output
                output = {"answer": output}
            step.status = "success"
            step.outputData = dumps(output)
            step.duration = int((time.perf_counter() - start) * 1000)
            step.updatedAt = datetime.utcnow()
            db.commit()
            await broker.publish(
                state.taskId,
                broker.make_event(
                    "step_success",
                    state.taskId,
                    {
                        "stepId": step.stepId,
                        "stepName": step.stepName,
                        "duration": step.duration,
                        "output": output,
                        "summary": step_summary(step.stepId, output),
                    },
                ),
            )
            return output
        except Exception as exc:
            step.status = "failed"
            step.errorMessage = str(exc)
            step.duration = int((time.perf_counter() - start) * 1000)
            db.commit()
            await broker.publish(state.taskId, broker.make_event("step_failed", state.taskId, {"stepId": step.stepId, "stepName": step.stepName, "errorMessage": str(exc)}))
            raise

    def _validate(self, state):
        if not state.description.strip():
            raise ValueError("问题描述不能为空")
        return {"valid": True, "riskLevel": state.riskLevel, "riskReason": risk_reason(state.symptoms)}

    def _load_field(self, db, state):
        field = db.get(CottonField, state.fieldId)
        state.fieldProfile = {"id": field.id, "name": field.name, "variety": field.variety, "area": field.area, "region": field.region, "growthStage": field.growthStage}
        return state.fieldProfile

    def _load_records(self, db, state):
        records = db.scalars(select(FarmRecord).where(FarmRecord.fieldId == state.fieldId).order_by(FarmRecord.operationDate)).all()
        state.historyRecords = [{"id": r.id, "actionCode": r.actionCode, "actionName": r.actionName, "operationDate": str(r.operationDate), "description": r.description} for r in records]
        return {"records": state.historyRecords}

    def _retrieve(self, state):
        state.knowledgeItems = self.knowledge.search(state.growthStage, state.symptoms, state.weatherTags, state.description)
        return {"items": state.knowledgeItems}

    def _recommend(self, state):
        state.recommendations = self.recommender.recommend(state.historyRecords, state.growthStage, state.knowledgeItems)
        return {"recommendations": state.recommendations}

    def _plan(self, state):
        state.farmPlan = self.recommender.build_plan(state.recommendations)
        return {"farmPlan": state.farmPlan}

    def _save_final(self, db, state):
        task = db.get(AgentTask, state.taskId)
        task.riskLevel = state.riskLevel
        task.farmPlan = dumps(state.farmPlan)
        task.evidences = dumps(state.knowledgeItems)
        task.finalAnswer = state.finalAnswer
        db.execute(delete(Recommendation).where(Recommendation.taskId == state.taskId))
        for item in state.recommendations:
            db.add(Recommendation(**recommendation_model_kwargs(state.taskId, item)))
        db.commit()
        return {"saved": True}

    async def _publish_and_store(self, db, state, event_type, data):
        task = db.get(AgentTask, state.taskId)
        if event_type == "farm_plan":
            task.farmPlan = dumps(data)
        elif event_type == "evidences":
            task.evidences = dumps(data)
        elif event_type == "recommendations":
            db.execute(delete(Recommendation).where(Recommendation.taskId == state.taskId))
            for item in data:
                db.add(Recommendation(**recommendation_model_kwargs(state.taskId, item)))
        elif event_type == "answer":
            task.finalAnswer = data["answer"]
        db.commit()
        await broker.publish(state.taskId, broker.make_event(event_type, state.taskId, data))
