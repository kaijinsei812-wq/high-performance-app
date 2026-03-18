from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, items, auth
from app.database import engine
from app import models
from app.middleware import log_requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    logger.info("🚀 High Performance App 起動完了")
    yield
    logger.info("👋 High Performance App 終了")


app = FastAPI(
    title="High Performance App",
    description="高性能APIサーバー - FastAPI / Python / PostgreSQL / JWT認証",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(log_requests)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
