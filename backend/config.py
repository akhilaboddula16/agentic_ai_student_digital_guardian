import os
from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./student_guardian.db")
ALLOWED_ORIGINS = _split_csv(os.getenv("ALLOWED_ORIGINS", "*"))
