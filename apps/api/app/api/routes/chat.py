from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import run_chat

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(body: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        return run_chat(
            db,
            body.question,
            retrieval_strategy=body.retrieval_strategy,
            use_query_rewrite=body.use_query_rewrite,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
