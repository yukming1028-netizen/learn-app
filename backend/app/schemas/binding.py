"""Binding schemas."""
from datetime import datetime
from pydantic import BaseModel


class DeviceGenerateRequest(BaseModel):
    device_uuid: str


class DeviceGenerateResponse(BaseModel):
    qr_token: str
    bind_code: str
    expires_at: str


class DeviceVerifyRequest(BaseModel):
    """Parent scans QR or enters code to link device to their account."""
    qr_token: str | None = None
    bind_code: str | None = None


class DeviceUnbindRequest(BaseModel):
    device_uuid: str


class DeviceBindResult(BaseModel):
    success: bool
    device_uuid: str = ""
    device_token: str = ""
    parent_email: str = ""
    children_count: int = 0
    message: str = ""


class DeviceStatusOut(BaseModel):
    bound: bool = False
    device_token: str = ""
    parent_email: str = ""
    children_count: int = 0


class DeviceCreateChildRequest(BaseModel):
    """Child device creates a new user."""
    name: str
    grade: int | None = 0
    avatar: str | None = "🐻"


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
