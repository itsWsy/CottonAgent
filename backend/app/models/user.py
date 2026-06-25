from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    passwordHash: Mapped[str] = mapped_column(String(255))
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    fields = relationship("CottonField", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("AgentTask", back_populates="user", cascade="all, delete-orphan")
