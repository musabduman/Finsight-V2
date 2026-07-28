from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChatRequest(BaseModel):
    question: str
    ticker: str | None = None  # ör. "THYAO" — verilirse RAG araması bu hisseyle filtrelenir