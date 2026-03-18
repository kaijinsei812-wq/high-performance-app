from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    created_at: Optional[datetime] = None

# In-memory store (後でDBに置き換え)
items_db: List[Item] = []
counter = 1

@router.get("/items", response_model=List[Item], tags=["Items"])
async def get_items():
    return items_db

@router.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="アイテムが見つかりません")

@router.post("/items", response_model=Item, tags=["Items"])
async def create_item(item: Item):
    global counter
    item.id = counter
    item.created_at = datetime.now()
    items_db.append(item)
    counter += 1
    return item

@router.put("/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(item_id: int, updated: Item):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            updated.id = item_id
            updated.created_at = item.created_at
            items_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="アイテムが見つかりません")

@router.delete("/items/{item_id}", tags=["Items"])
async def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(i)
            return {"message": "削除しました"}
    raise HTTPException(status_code=404, detail="アイテムが見つかりません")
