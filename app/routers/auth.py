from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.UserResponse)
async def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="このユーザー名は既に使用されています")
    user = models.User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=auth.get_password_hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="ユーザー名またはパスワードが間違っています")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
async def me(current_user=Depends(auth.get_current_user)):
    return current_user
