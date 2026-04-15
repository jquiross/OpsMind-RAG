from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.eval_run import EvalRun

router = APIRouter()


@router.get("/eval/runs")
def list_eval_runs(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(EvalRun).order_by(EvalRun.created_at.desc()).limit(20)).all()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "dataset_name": r.dataset_name,
            "created_at": r.created_at.isoformat(),
            "metrics_json": r.metrics_json,
        }
        for r in rows
    ]
