from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, chat, documents, eval_routes, health, ingest
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import engine
import app.models  # noqa: F401  # register models

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(get_settings().log_level)
    logger.info("startup", environment=get_settings().environment)
    yield
    engine.dispose()
    logger.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="OpsMind RAG API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    app.include_router(ingest.router, prefix="/api", tags=["ingest"])
    app.include_router(documents.router, prefix="/api", tags=["documents"])
    app.include_router(analytics.router, prefix="/api", tags=["analytics"])
    app.include_router(eval_routes.router, prefix="/api", tags=["eval"])
    return app


app = create_app()
