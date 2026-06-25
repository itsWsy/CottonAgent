from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    fieldId: Mapped[int] = mapped_column(ForeignKey("cotton_fields.id", ondelete="CASCADE"), index=True)
    description: Mapped[str] = mapped_column(Text)
    growthStage: Mapped[str] = mapped_column(String(30))
    symptoms: Mapped[str] = mapped_column(Text, default="[]")
    weatherTags: Mapped[str] = mapped_column(Text, default="[]")
    riskLevel: Mapped[str] = mapped_column(String(20), default="low")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    decision: Mapped[str] = mapped_column(String(20), default="pending")
    farmPlan: Mapped[str] = mapped_column(Text, default="[]")
    evidences: Mapped[str] = mapped_column(Text, default="[]")
    finalAnswer: Mapped[str] = mapped_column(Text, default="")
    errorMessage: Mapped[str] = mapped_column(Text, default="")
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completedAt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="tasks")
    field = relationship("CottonField", back_populates="tasks")
    steps = relationship("AgentStep", back_populates="task", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="task", cascade="all, delete-orphan")
