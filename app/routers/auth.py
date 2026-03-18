from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app import models, schemas, auth
from app.limiter import limiter
from app.metrics import user_registrations_total, login_failures_total

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=schemas.UserResponse)
@limiter.limit("5/minute")
def register(request: Request, user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="このメールアドレスはすでに登録されています")
    user = models.User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=auth.get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_registrations_total.inc()
    return user


@router.post("/token", response_model=TokenPair)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        login_failures_total.inc()
        raise HTTPException(status_code=401, detail="ユーザー名またはパスワードが正しくありません")
    access_token = auth.create_access_token({"sub": user.username})
    refresh_token = auth.create_refresh_token({"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.Token)
@limiter.limit("20/minute")
def refresh(request: Request, body: RefreshRequest, db: Session = Depends(get_db)):
    from jose import JWTError, jwt
    credentials_exception = HTTPException(status_code=401, detail="リフレッシュトークンが無効です")
    if auth.is_token_blacklisted(body.refresh_token):
        raise credentials_exception
    try:
        payload = jwt.decode(body.refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise credentials_exception
    # 古いリフレッシュトークンをブラックリストへ
    auth.blacklist_token(body.refresh_token)
    new_access = auth.create_access_token({"sub": user.username})
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/logout")
def logout(
    body: RefreshRequest,
    current_user: models.User = Depends(auth.get_current_user),
):
    auth.blacklist_token(body.refresh_token)
    return {"message": "ログアウトしました"}


@router.get("/me", response_model=schemas.UserResponse)
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
