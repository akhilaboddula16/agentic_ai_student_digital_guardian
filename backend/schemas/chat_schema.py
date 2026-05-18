from pydantic import BaseModel


class ChatRequest(BaseModel):
    student_id: int
    question: str
