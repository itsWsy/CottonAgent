from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CottonField(Base):
    __tablename__ = "cotton_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    variety: Mapped[str] = mapped_column(String(100))
    area: Mapped[float] = mapped_column(Float)
    region: Mapped[str] = mapped_column(String(100))
    growthStage: Mapped[str] = mapped_column(String(30))
    sowingDate: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="fields")
    records = relationship("FarmRecord", back_populates="field", cascade="all, delete-orphan")
    tasks = relationship("AgentTask", back_populates="field", cascade="all, delete-orphan")
