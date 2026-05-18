from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.chat_schema import ChatRequest
from backend.services.usage_service import get_usage_summary
from backend.services.gemini_service import ask_gemini

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])


@router.post("/ask")
def ask_chatbot(data: ChatRequest, db: Session = Depends(get_db)):
    summary = get_usage_summary(db, data.student_id)
    answer = ask_gemini(data.question, summary)
    return {"question": data.question, "usage_summary": summary, "answer": answer}
