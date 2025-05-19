from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    provider: str
    provider_id: str

class User(UserBase):
    id: int
    provider: str

    class Config:
        orm_mode = True