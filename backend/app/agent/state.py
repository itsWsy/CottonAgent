from dataclasses import dataclass, field


@dataclass
class AgentState:
    taskId: str
    userId: int
    fieldId: int
    description: str
    growthStage: str
    symptoms: list[str]
    weatherTags: list[str]
    fieldProfile: dict | None = None
    historyRecords: list[dict] = field(default_factory=list)
    knowledgeItems: list[dict] = field(default_factory=list)
    recommendations: list[dict] = field(default_factory=list)
    farmPlan: list[dict] = field(default_factory=list)
    riskLevel: str = "low"
    finalAnswer: str = ""
    errors: list[str] = field(default_factory=list)
