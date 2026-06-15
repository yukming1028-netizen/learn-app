"""Binding schemas — device generates code, parent consumes it."""
from datetime import datetime
from pydantic import BaseModel


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


class DeviceUnbindRequest(BaseModel):
    """Child device unbinds a specific child profile."""
    device_uuid: str
    child_id: int


class BindResult(BaseModel):
    success: bool
    child_id: int | None = None
    child_name: str = ""
    device_uuid: str = ""
    welcome_message: str = ""


class DeviceChildOut(BaseModel):
    """Child profile as seen from a device."""
    id: int
    name: str
    avatar: str
    parent_email: str = ""
    total_questions: int = 0
    total_correct: int = 0

    class Config:
        from_attributes = True
