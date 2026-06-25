from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taskId: Mapped[str] = mapped_column(ForeignKey("agent_tasks.id", ondelete="CASCADE"), index=True)
    stepId: Mapped[str] = mapped_column(String(80))
    stepName: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20), default="waiting")
    inputData: Mapped[str] = mapped_column(Text, default="{}")
    outputData: Mapped[str] = mapped_column(Text, default="{}")
    errorMessage: Mapped[str] = mapped_column(Text, default="")
    duration: Mapped[int] = mapped_column(Integer, default=0)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    task = relationship("AgentTask", back_populates="steps")
