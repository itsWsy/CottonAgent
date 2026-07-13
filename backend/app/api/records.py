from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.responses import ok
from app.core.security import get_current_user
from app.database.session import get_db
from app.models import CottonField, FarmRecord, User
from app.schemas.record import RecordCreate, RecordOut

router = APIRouter(tags=["records"])


def ensure_field(db: Session, field_id: int, user_id: int) -> CottonField:
    field = db.scalar(select(CottonField).where(CottonField.id == field_id, CottonField.userId == user_id))
    if not field:
        raise HTTPException(status_code=404, detail="棉田不存在")
    return field


def ensure_record(db: Session, record_id: int, user_id: int) -> FarmRecord:
    record = db.get(FarmRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    ensure_field(db, record.fieldId, user_id)
    return record


@router.get("/fields/{field_id}/records")
def list_records(field_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ensure_field(db, field_id, user.id)
    records = db.scalars(select(FarmRecord).where(FarmRecord.fieldId == field_id).order_by(FarmRecord.operationDate.desc())).all()
    return ok([RecordOut.model_validate(r).model_dump() for r in records])


@router.post("/fields/{field_id}/records")
def create_record(field_id: int, payload: RecordCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ensure_field(db, field_id, user.id)
    record = FarmRecord(fieldId=field_id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return ok(RecordOut.model_validate(record).model_dump())


@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = ensure_record(db, record_id, user.id)
    db.delete(record)
    db.commit()
    return ok(True)
