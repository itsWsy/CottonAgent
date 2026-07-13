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

SAFETY_CONSTRAINTS = [
    "仅生成监测、采样、记录、巡查、复查、评估类辅助建议。",
    "不生成具体农药名称、剂量或自动执行处置建议。",
    "中高风险结果必须提示专业人员复核。",
    "所有推荐均需人工确认后才能用于实际农事操作。",
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


def make_tool_call(tool_name: str, tool_input: dict, observation: dict | list | str) -> dict:
    return {
        "toolName": tool_name,
        "toolInput": tool_input,
        "observation": observation,
        "calledAt": datetime.utcnow().isoformat(),
    }


def task_to_detail(task: AgentTask) -> dict:
    symptoms = loads(task.symptoms, [])
    steps = [step_to_out(s) for s in sorted(task.steps, key=lambda x: x.id)]
    return {
        "id": task.id,
        "fieldId": task.fieldId,
        "fieldName": task.field.name if task.field else None,
        "description": task.description,
        "growthStage": task.growthStage,
        "symptoms": symptoms,
        "weatherTags": loads(task.weatherTags, []),
        "riskLevel": task.riskLevel,
        "riskReason": risk_reason(symptoms),
        "safetyConstraints": SAFETY_CONSTRAINTS,
        "agentTrace": [step["toolCall"] for step in steps if step.get("toolCall")],
        "status": task.status,
        "decision": task.decision,
        "farmPlan": loads(task.farmPlan, []),
        "evidences": loads(task.evidences, []),
        "finalAnswer": task.finalAnswer,
        "errorMessage": task.errorMessage,
        "createdAt": task.createdAt,
        "completedAt": task.completedAt,
        "steps": steps,
        "recommendations": [rec_to_out(r) for r in task.recommendations],
    }


def step_summary(step_id: str, output: dict | list | str | None) -> str:
    observation = output.get("toolCall", {}).get("observation", output) if isinstance(output, dict) else output
    if step_id == "validate_input":
        return "咨询信息、风险规则和安全边界已校验。"
    if step_id == "load_field_context" and isinstance(observation, dict):
        return f"已读取“{observation.get('name', '棉田')}”档案。"
    if step_id == "load_history_records" and isinstance(observation, dict):
        return f"已获取 {len(observation.get('records', []))} 条历史农事记录。"
    if step_id == "retrieve_knowledge" and isinstance(observation, dict):
        return f"已检索到 {len(observation.get('items', []))} 条相关知识。"
    if step_id == "recommend_next_actions" and isinstance(observation, dict):
        return f"已生成 {len(observation.get('recommendations', []))} 条可解释推荐。"
    if step_id == "generate_farm_plan" and isinstance(observation, dict):
        return f"已生成 {len(observation.get('farmPlan', []))} 个 7 天计划项。"
    if step_id == "generate_final_answer":
        return "最终说明已生成，并附带安全免责声明。"
    if step_id == "save_task_result":
        return "任务结果已持久化，可刷新恢复。"
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
        "toolCall": output.get("toolCall") if isinstance(output, dict) else None,
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
        "candidateSources": loads(rec.candidateSources, []),
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
        "candidateSources": dumps(item.get("candidateSources", [])),
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
                riskReason=risk_reason(loads(task.symptoms, [])),
                safetyConstraints=SAFETY_CONSTRAINTS,
            )
            await self._run_step(db, state, "validate_input", {"description": state.description, "symptoms": state.symptoms, "weatherTags": state.weatherTags}, lambda: self._validate(state))
            await self._run_step(db, state, "load_field_context", {"fieldId": state.fieldId}, lambda: self._load_field(db, state))
            await self._run_step(db, state, "load_history_records", {"fieldId": state.fieldId}, lambda: self._load_records(db, state))
            await self._run_step(db, state, "retrieve_knowledge", {"growthStage": state.growthStage, "symptoms": state.symptoms, "weatherTags": state.weatherTags}, lambda: self._retrieve(state))
            await self._run_step(db, state, "recommend_next_actions", {"contextReady": True}, lambda: self._recommend(state))
            await self._publish_and_store(db, state, "recommendations", state.recommendations)
            await self._run_step(db, state, "generate_farm_plan", {"recommendationCount": len(state.recommendations)}, lambda: self._plan(state))
            await self._publish_and_store(db, state, "farm_plan", state.farmPlan)
            await self._publish_and_store(db, state, "evidences", state.knowledgeItems)
            await self._run_step_async(db, state, "generate_final_answer", {"useLLMWhenConfigured": True}, lambda: self.llm.generate_answer(self._answer_context(state)))
            await self._publish_and_store(db, state, "answer", {"answer": state.finalAnswer})
            await self._run_step(db, state, "save_task_result", {"persist": ["steps", "recommendations", "plan", "evidences", "answer"]}, lambda: self._save_final(db, state))
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
                output = self._tool_output("final_answer_generator", input_data, {"answer": output})
            step.status = "success"
            step.outputData = dumps(output)
            step.duration = int((time.perf_counter() - start) * 1000)
            step.updatedAt = datetime.utcnow()
            db.commit()
            await broker.publish(
                state.taskId,
                broker.make_event("step_success", state.taskId, {"stepId": step.stepId, "stepName": step.stepName, "duration": step.duration, "output": output, "summary": step_summary(step.stepId, output)}),
            )
            return output
        except Exception as exc:
            step.status = "failed"
            step.errorMessage = str(exc)
            step.duration = int((time.perf_counter() - start) * 1000)
            db.commit()
            await broker.publish(state.taskId, broker.make_event("step_failed", state.taskId, {"stepId": step.stepId, "stepName": step.stepName, "errorMessage": str(exc)}))
            raise

    def _tool_output(self, tool_name: str, tool_input: dict, observation: dict | list | str) -> dict:
        return {"toolCall": make_tool_call(tool_name, tool_input, observation)}

    def _validate(self, state):
        if not state.description.strip():
            raise ValueError("问题描述不能为空")
        observation = {"valid": True, "riskLevel": state.riskLevel, "riskReason": state.riskReason, "safetyConstraints": state.safetyConstraints}
        return self._tool_output("consultation_validator", {"description": state.description, "symptoms": state.symptoms, "weatherTags": state.weatherTags}, observation)

    def _load_field(self, db, state):
        field = db.get(CottonField, state.fieldId)
        state.fieldProfile = {"id": field.id, "name": field.name, "variety": field.variety, "area": field.area, "region": field.region, "growthStage": field.growthStage}
        return self._tool_output("field_profile_reader", {"fieldId": state.fieldId}, state.fieldProfile)

    def _load_records(self, db, state):
        records = db.scalars(select(FarmRecord).where(FarmRecord.fieldId == state.fieldId).order_by(FarmRecord.operationDate)).all()
        state.historyRecords = [{"id": r.id, "actionCode": r.actionCode, "actionName": r.actionName, "operationDate": str(r.operationDate), "description": r.description} for r in records]
        return self._tool_output("farm_record_reader", {"fieldId": state.fieldId}, {"records": state.historyRecords})

    def _retrieve(self, state):
        state.knowledgeItems = self.knowledge.search(state.growthStage, state.symptoms, state.weatherTags, state.description)
        return self._tool_output("cotton_knowledge_retriever", {"growthStage": state.growthStage, "symptoms": state.symptoms, "weatherTags": state.weatherTags}, {"items": state.knowledgeItems})

    def _recommend(self, state):
        state.recommendations = self.recommender.recommend(state.historyRecords, state.growthStage, state.knowledgeItems, state.symptoms, state.weatherTags)
        return self._tool_output("multi_factor_recommender", {"historyCount": len(state.historyRecords), "knowledgeCount": len(state.knowledgeItems)}, {"recommendations": state.recommendations})

    def _plan(self, state):
        state.farmPlan = self.recommender.build_plan(state.recommendations)
        return self._tool_output("seven_day_plan_generator", {"recommendations": [item["actionCode"] for item in state.recommendations]}, {"farmPlan": state.farmPlan})

    def _answer_context(self, state) -> dict:
        return {
            "fieldProfile": state.fieldProfile,
            "historyRecords": state.historyRecords[-5:],
            "growthStage": state.growthStage,
            "symptoms": state.symptoms,
            "weatherTags": state.weatherTags,
            "riskLevel": state.riskLevel,
            "riskReason": state.riskReason,
            "recommendations": state.recommendations,
            "farmPlan": state.farmPlan,
            "evidences": state.knowledgeItems,
            "safetyConstraints": state.safetyConstraints,
        }

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
        return self._tool_output("task_result_persister", {"taskId": state.taskId}, {"saved": True})

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
