"""Report schemas."""
from pydantic import BaseModel


class ReportRequest(BaseModel):
    child_id: int
    period_days: int = 30
