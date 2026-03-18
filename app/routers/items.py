from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/", response_model=List[schemas.ItemResponse])
async def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Item).offset(skip).limit(limit).all()

@router.get("/{item_id}", response_model=schemas.ItemResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    return item

@router.post("/", response_model=schemas.ItemResponse)
async def create_item(item_in: schemas.ItemCreate, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    item = models.Item(**item_in.model_dump(), owner_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/{item_id}", response_model=schemas.ItemResponse)
async def update_item(item_id: int, item_in: schemas.ItemUpdate, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    item = db.query(models.Item).filter(models.Item.id == item_id, models.Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    for k, v in item_in.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    item = db.query(models.Item).filter(models.Item.id == item_id, models.Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    db.delete(item)
    db.commit()
    return {"message": "削除しました"}
