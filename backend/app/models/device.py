"""Device model — links a device to a parent with auth token."""
import secrets
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def _generate_device_token():
    return secrets.token_hex(16)  # 32-char hex


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_uuid = Column(String(64), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False, index=True)
    device_token = Column(String(64), unique=True, default=_generate_device_token, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    bound_at = Column(DateTime, default=datetime.utcnow)
    unbound_at = Column(DateTime, nullable=True)

    parent = relationship("Parent", backref="devices")

    def invalidate(self):
        """Invalidate the device token (called on unbind)."""
        self.is_active = False
        self.unbound_at = datetime.utcnow()
        # Generate a new token so old one can never be reused
        self.device_token = _generate_device_token()
