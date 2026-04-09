from datetime import datetime
from typing import List

from authx import AuthX, AuthXConfig, TokenPayload
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session


from src.database import get_db
from src.auth.models import User
from src.auth.schemas import UserRegisterSchema, UserSchema


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
def register_user(
    user_data: UserRegisterSchema, 
    db: Session = Depends(get_db)
):

    new_user = User(email=user_data.email,password=user_data.password, first_name="New", last_name="User")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered", "email": new_user.email}


@user_router.post("/login")
def login(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=user_data.email, password=user_data.password).first()
    
    if not user:
        raise HTTPException(401, "Invalid credentials")
        
    return {"access_token": auth.create_access_token(uid=user.email)}


@user_router.get("/protected")
def protected(payload: TokenPayload = Depends(auth.access_token_required), credentials = Depends(security)):
    return {
        "message": "Welcome to protected route!", "user_id": payload.sub
        }