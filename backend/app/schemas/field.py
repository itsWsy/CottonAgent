from datetime import date, datetime

from pydantic import BaseModel, Field


class FieldBase(BaseModel):
    name: str
    variety: str
    area: float = Field(gt=0)
    region: str
    growthStage: str
    sowingDate: date | None = None
    description: str = ""


class FieldCreate(FieldBase):
    pass


class FieldUpdate(FieldBase):
    pass


class FieldOut(FieldBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}
