"""Report routes: PDF report download (V2)."""
from datetime import datetime, timezone
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
from app.database import get_db
from app.models.parent import Parent
from app.models.child import Child
from app.services.report_service import generate_report_pdf
from app.routers.deps import get_current_parent

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{child_id}/pdf")
def download_report(
    child_id: int,
    period_days: int = 30,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent.id).first()
    if not child:
        raise HTTPException(status_code=404, detail="找不到子女")

    pdf_bytes = generate_report_pdf(db, child, period_days)

    filename = f"{child.name}_report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"
    filename_encoded = quote(filename)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"report.pdf\"; filename*=UTF-8''{filename_encoded}"},
    )
