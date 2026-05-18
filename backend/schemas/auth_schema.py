from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # parent or student


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PairRequest(BaseModel):
    parent_id: int
    pair_code: str
