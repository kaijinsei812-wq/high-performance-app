from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, items, auth
from app.database import engine
from app import models
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# DB tables auto-create
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="High Performance App",
    description="高性能APIサーバー - FastAPI / Python",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 High Performance App 起動完了")
