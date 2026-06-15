"""Auth schemas."""
from pydantic import BaseModel, EmailStr, field_validator


class ParentCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("密碼至少需要6個字符")
        return v


class ParentLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ParentOut(BaseModel):
    id: int
    email: str
    email_verified: bool

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id: int | None = None
