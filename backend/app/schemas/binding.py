"""Binding schemas."""
from pydantic import BaseModel


class QRGenerateResponse(BaseModel):
    qr_token: str
    expires_at: str
    parent_id: int


class QRVerifyRequest(BaseModel):
    qr_token: str
    device_uuid: str
    child_name: str = "小寶貝"


class BindResult(BaseModel):
    success: bool
    child_id: int | None = None
    child_name: str = ""
    welcome_message: str = ""
