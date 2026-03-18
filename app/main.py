from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.routers import health, items, auth
from app.database import engine
from app import models
from app.middleware import log_requests
from app.limiter import limiter
from app.metrics import setup_metrics
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
    description="高性能APIサーバー - FastAPI / Python / PostgreSQL / JWT認証 / Redis / Prometheus",
    version="3.0.0",
    lifespan=lifespan,
)

# レート制限
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(log_requests)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")

# Prometheusメトリクス (/metrics エンドポイント追加)
setup_metrics(app)
