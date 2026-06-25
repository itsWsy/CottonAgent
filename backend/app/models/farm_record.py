from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FarmRecord(Base):
    __tablename__ = "farm_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fieldId: Mapped[int] = mapped_column(ForeignKey("cotton_fields.id", ondelete="CASCADE"), index=True)
    actionCode: Mapped[str] = mapped_column(String(50))
    actionName: Mapped[str] = mapped_column(String(100))
    operationDate: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text, default="")
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    field = relationship("CottonField", back_populates="records")
