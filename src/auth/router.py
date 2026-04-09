from datetime import datetime
from typing import List

from authx import AuthX, AuthXConfig, TokenPayload
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session


from src.database import get_db
from src.auth.models import User
from src.auth.schemas import UserRegisterSchema, UserLoginSchema


config = AuthXConfig(
    JWT_SECRET_KEY="test-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
security = HTTPBearer()

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@user_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User already exists" 
        )

    new_user = User(
        email=user_data.email,
        password=user_data.password, 
        first_name="User", 
        last_name="New"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered", "email": new_user.email}

@user_router.post("/login")
def login(user_data: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=user_data.email, password=user_data.password).first()
    
    if not user:
        raise HTTPException(401, "Invalid credentials")
        
    access_token = auth.create_access_token(uid=user.email)
    refresh_token = auth.create_refresh_token(uid=user.email)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@user_router.post("/refresh")
def refresh(
    payload: TokenPayload = Depends(auth.refresh_token_required),
    credentials = Depends(security)
):
    new_access_token = auth.create_access_token(uid=payload.sub)
    return {"access_token": new_access_token}

@user_router.get("/protected")
def protected(payload: TokenPayload = Depends(auth.access_token_required), credentials = Depends(security)):
    return {
        "message": "Welcome to protected route!", "user_id": payload.sub
        }