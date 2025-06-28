from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None

class UserCreate(UserBase):
    provider: str
    provider_id: str
    picture: Optional[str] = None

class User(UserBase):
    id: int
    provider: str
    provider_id: str
    picture: Optional[str] = None

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    user: User