from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.feedback import FeedbackCreate
from app.models.query import Feedback
from app.services.analytics_service import dashboard_summary
import uuid

router = APIRouter()


@router.get("/analytics/dashboard")
def analytics_dashboard(db: Session = Depends(get_db)) -> dict:
    return dashboard_summary(db)


@router.post("/feedback")
def submit_feedback(body: FeedbackCreate, db: Session = Depends(get_db)) -> dict:
    fb = Feedback(
        id=uuid.uuid4(),
        query_id=body.query_id,
        rating=body.rating,
        comment=body.comment,
    )
    db.add(fb)
    db.commit()
    return {"status": "ok", "id": str(fb.id)}
