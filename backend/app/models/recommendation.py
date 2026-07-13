from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taskId: Mapped[str] = mapped_column(ForeignKey("agent_tasks.id", ondelete="CASCADE"), index=True)
    actionCode: Mapped[str] = mapped_column(String(50))
    actionName: Mapped[str] = mapped_column(String(100))
    score: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text)
    scoreBreakdown: Mapped[str] = mapped_column(Text, default="{}")
    reasonItems: Mapped[str] = mapped_column(Text, default="[]")
    candidateSources: Mapped[str] = mapped_column(Text, default="[]")
    expectedDay: Mapped[int] = mapped_column(Integer)
    sourceType: Mapped[str] = mapped_column(String(50))
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    task = relationship("AgentTask", back_populates="recommendations")
