from pydantic import BaseModel


class DashboardSummary(BaseModel):
    fieldCount: int
    weeklyTaskCount: int
    pendingDecisionCount: int
    mediumHighRiskCount: int
