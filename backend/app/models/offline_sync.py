"""Offline sync models: cached answer records pending upload."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from app.database import Base


class OfflineSyncLog(Base):
    """Tracks offline answer sync operations from child devices."""
    __tablename__ = "offline_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    device_uuid = Column(String(100), nullable=True)
    batch_id = Column(String(36), nullable=False, index=True)  # UUID per batch
    records_count = Column(Integer, default=0)
    accepted_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)  # duplicates
    synced_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="completed")  # completed, partial, failed
    details = Column(JSON, default=list)  # per-record status
