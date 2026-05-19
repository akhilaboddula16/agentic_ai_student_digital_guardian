from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # parent or student
    invite_code: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PairRequest(BaseModel):
    pair_code: str
