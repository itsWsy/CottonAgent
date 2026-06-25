from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.responses import ok
from app.core.security import get_current_user
from app.database.session import get_db
from app.models import CottonField, User
from app.schemas.field import FieldCreate, FieldOut, FieldUpdate

router = APIRouter(prefix="/fields", tags=["fields"])


@router.get("")
def list_fields(name: str = "", growthStage: str = "", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(CottonField).where(CottonField.userId == user.id).order_by(CottonField.createdAt.desc())
    if name:
        stmt = stmt.where(CottonField.name.contains(name))
    if growthStage:
        stmt = stmt.where(CottonField.growthStage == growthStage)
    return ok([FieldOut.model_validate(x).model_dump() for x in db.scalars(stmt).all()])


@router.post("")
def create_field(payload: FieldCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field = CottonField(userId=user.id, **payload.model_dump())
    db.add(field)
    db.commit()
    db.refresh(field)
    return ok(FieldOut.model_validate(field).model_dump())


@router.get("/{field_id}")
def get_field(field_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field = db.scalar(select(CottonField).where(CottonField.id == field_id, CottonField.userId == user.id))
    if not field:
        raise HTTPException(status_code=404, detail="棉田不存在")
    return ok(FieldOut.model_validate(field).model_dump())


@router.put("/{field_id}")
def update_field(field_id: int, payload: FieldUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field = db.scalar(select(CottonField).where(CottonField.id == field_id, CottonField.userId == user.id))
    if not field:
        raise HTTPException(status_code=404, detail="棉田不存在")
    for key, value in payload.model_dump().items():
        setattr(field, key, value)
    db.commit()
    db.refresh(field)
    return ok(FieldOut.model_validate(field).model_dump())


@router.delete("/{field_id}")
def delete_field(field_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field = db.scalar(select(CottonField).where(CottonField.id == field_id, CottonField.userId == user.id))
    if not field:
        raise HTTPException(status_code=404, detail="棉田不存在")
    db.delete(field)
    db.commit()
    return ok(True)
