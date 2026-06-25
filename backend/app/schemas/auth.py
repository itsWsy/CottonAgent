from datetime import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    createdAt: datetime

    model_config = {"from_attributes": True}


class LoginOut(BaseModel):
    token: str
    userInfo: UserOut
