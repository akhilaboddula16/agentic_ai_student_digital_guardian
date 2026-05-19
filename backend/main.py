from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import ALLOWED_ORIGINS
from backend.database import Base, engine
from backend.models.user_model import User, ParentStudentPair
from backend.models.token_model import AuthToken
from backend.models.usage_model import AppUsage
from backend.models.alert_model import Alert
from backend.routes.admin_routes import router as admin_router
from backend.routes.auth_routes import router as auth_router
from backend.routes.usage_routes import router as usage_router
from backend.routes.alert_routes import router as alert_router
from backend.routes.chatbot_routes import router as chatbot_router
from backend.routes.report_routes import router as report_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic AI Student Digital Guardian",
    description="Fresher-friendly agentic AI project with app usage tracking simulation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(usage_router)
app.include_router(alert_router)
app.include_router(chatbot_router)
app.include_router(report_router)
app.include_router(admin_router)


@app.get("/")
def home():
    return {"message": "Student Digital Guardian backend is running"}


@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}
