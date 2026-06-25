from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AgentTaskCreate(BaseModel):
    fieldId: int
    growthStage: str
    symptoms: list[str] = []
    weatherTags: list[str] = []
    description: str


class AgentStepOut(BaseModel):
    stepId: str
    name: str
    status: str
    startTime: datetime | None = None
    endTime: datetime | None = None
    duration: int = 0
    input: Any = None
    output: Any = None
    errorMessage: str = ""


class RecommendationOut(BaseModel):
    actionCode: str
    actionName: str
    score: float
    scoreBreakdown: dict = {}
    expectedDay: int
    reason: str
    reasonItems: list[str] = []
    sourceType: str


class AgentTaskOut(BaseModel):
    id: str
    fieldId: int
    fieldName: str | None = None
    description: str
    growthStage: str
    symptoms: list[str]
    weatherTags: list[str]
    riskLevel: str
    riskReason: str = ""
    status: str
    decision: str
    farmPlan: list[dict]
    evidences: list[dict]
    finalAnswer: str
    errorMessage: str
    createdAt: datetime
    completedAt: datetime | None = None
    steps: list[AgentStepOut] = []
    recommendations: list[RecommendationOut] = []
