from pydantic import BaseModel


class UsageCreate(BaseModel):
    student_id: int
    app_name: str
    duration_minutes: int
    limit_minutes: int = 60


class DeviceUsageSyncRequest(BaseModel):
    app_name: str
    duration_minutes: int
    limit_minutes: int = 60
