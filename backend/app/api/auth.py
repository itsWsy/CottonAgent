from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.responses import ok
from app.core.security import create_token, get_current_user, verify_password
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.passwordHash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return ok(LoginOut(token=create_token(user), userInfo=UserOut.model_validate(user)).model_dump())


@router.get("/profile")
def profile(user: User = Depends(get_current_user)):
    return ok(UserOut.model_validate(user).model_dump())
