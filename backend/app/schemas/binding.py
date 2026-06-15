"""Binding schemas — device generates code, parent consumes it."""
from datetime import datetime
from pydantic import BaseModel

# Grade options: 0=學前預備, 1-6=小一至小六
GRADE_OPTIONS = [
    {"value": 0, "label": "小一學前預備"},
    {"value": 1, "label": "小一"},
    {"value": 2, "label": "小二"},
    {"value": 3, "label": "小三"},
    {"value": 4, "label": "小四"},
    {"value": 5, "label": "小五"},
    {"value": 6, "label": "小六"},
]


class DeviceGenerateRequest(BaseModel):
    device_uuid: str


class DeviceGenerateResponse(BaseModel):
    qr_token: str
    bind_code: str
    expires_at: str


class DeviceBindRequest(BaseModel):
    """Parent scans QR or enters code to bind a device."""
    qr_token: str | None = None
    bind_code: str | None = None
    child_name: str = "小寶貝"
    grade: int = 0  # 0=學前預備, 1-6=小一至小六


class DeviceUnbindRequest(BaseModel):
    """Child device unbinds a specific child profile."""
    device_uuid: str
    child_id: int


class BindResult(BaseModel):
    success: bool
    child_id: int | None = None
    child_name: str = ""
    grade: int = 0
    grade_label: str = ""
    device_uuid: str = ""
    welcome_message: str = ""


class DeviceChildOut(BaseModel):
    """Child profile as seen from a device."""
    id: int
    name: str
    avatar: str
    grade: int = 0
    grade_label: str = ""
    parent_email: str = ""
    total_questions: int = 0
    total_correct: int = 0

    class Config:
        from_attributes = True
