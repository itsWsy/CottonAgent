from datetime import date, datetime

from pydantic import BaseModel


class RecordCreate(BaseModel):
    actionCode: str
    actionName: str
    operationDate: date
    description: str = ""


class RecordOut(RecordCreate):
    id: int
    fieldId: int
    createdAt: datetime

    model_config = {"from_attributes": True}
