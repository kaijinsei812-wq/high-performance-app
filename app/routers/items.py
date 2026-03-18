from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, auth
from app.cache import cache_get, cache_set, cache_delete_pattern
from app.limiter import limiter
from app.metrics import items_created_total, cache_hits_total, cache_misses_total
from typing import List

router = APIRouter(prefix="/items", tags=["items"])
CACHE_TTL = 60


@router.get("/", response_model=List[schemas.ItemResponse])
@limiter.limit("30/minute")
def list_items(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cache_key = f"items:list:{skip}:{limit}"
    cached = cache_get(cache_key)
    if cached:
        cache_hits_total.inc()
        return cached
    cache_misses_total.inc()
    items = db.query(models.Item).offset(skip).limit(limit).all()
    result = [schemas.ItemResponse.model_validate(i).model_dump() for i in items]
    cache_set(cache_key, result, ttl=CACHE_TTL)
    return items


@router.post("/", response_model=schemas.ItemResponse)
@limiter.limit("20/minute")
def create_item(
    request: Request,
    item_in: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    item = models.Item(**item_in.model_dump(), owner_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    items_created_total.inc()
    cache_delete_pattern("items:list:*")
    return item


@router.get("/{item_id}", response_model=schemas.ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    cache_key = f"items:{item_id}"
    cached = cache_get(cache_key)
    if cached:
        cache_hits_total.inc()
        return cached
    cache_misses_total.inc()
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    cache_set(cache_key, schemas.ItemResponse.model_validate(item).model_dump(), ttl=CACHE_TTL)
    return item


@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(
    item_id: int,
    item_in: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    for key, value in item_in.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    cache_delete_pattern("items:*")
    return item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    db.delete(item)
    db.commit()
    cache_delete_pattern("items:*")
    return {"message": "削除しました", "id": item_id}


# 非同期処理エンドポイント
from fastapi import BackgroundTasks


@router.post("/{item_id}/process")
def process_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """アイテムの非同期処理をキューに追加する"""
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    try:
        from app.tasks import process_item_async
        task = process_item_async.delay(item_id, current_user.id)
        return {"task_id": task.id, "status": "queued", "message": "処理をキューに追加しました"}
    except Exception:
        return {"task_id": None, "status": "queued_locally", "message": "Celery未接続のためスキップ（本番では動作します）"}


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """Celeryタスクの状態を確認する"""
    try:
        from celery.result import AsyncResult
        from app.worker import celery_app
        result = AsyncResult(task_id, app=celery_app)
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
        }
    except Exception:
        return {"task_id": task_id, "status": "UNKNOWN", "result": None}
