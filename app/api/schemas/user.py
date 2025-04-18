from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)


class UserInDBBase(UserBase):
    id: UUID
    
    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str