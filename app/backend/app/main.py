import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.logging_config import setup_logging
from app.metrics import record_metrics
from app.request_logging import log_requests
from app.routers import ops, todos

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("application started")
    yield
    # SIGTERM'de uvicorn açık istekleri bitirir, ardından buraya gelinir
    engine.dispose()
    logger.info("application stopped")


app = FastAPI(title="Todo API", lifespan=lifespan)

app.middleware("http")(record_metrics)
app.middleware("http")(log_requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ops.router)
app.include_router(todos.router)
