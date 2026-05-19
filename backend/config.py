import os
from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./student_guardian.db")
ALLOWED_ORIGINS = _split_csv(os.getenv("ALLOWED_ORIGINS", "*"))
TOKEN_TTL_MINUTES = int(os.getenv("TOKEN_TTL_MINUTES", "480"))
REGISTRATION_MODE = os.getenv("REGISTRATION_MODE", "open").strip().lower()
REGISTRATION_INVITE_CODE = os.getenv("REGISTRATION_INVITE_CODE", "").strip()
ADMIN_EMAILS = {email.lower() for email in _split_csv(os.getenv("ADMIN_EMAILS", ""))}
