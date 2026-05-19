from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user_model import User
from backend.schemas.chat_schema import ChatRequest
from backend.security import ensure_student_access, get_current_user
from backend.services.usage_service import get_usage_summary
from backend.services.llm_service import ask_llm

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])


@router.post("/ask")
def ask_chatbot(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_student_access(db, current_user, data.student_id)
    summary = get_usage_summary(db, data.student_id)
    answer = ask_llm(data.question, summary)
    return {"question": data.question, "usage_summary": summary, "answer": answer}
