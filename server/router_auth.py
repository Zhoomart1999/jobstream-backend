from fastapi import APIRouter, HTTPException, Depends, Request
from models import User, UserRole
from auth import create_access_token, verify_telegram_auth
import os
from pydantic import BaseModel, EmailStr
from typing import Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["auth"])

class TelegramLoginRequest(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str

@router.post("/telegram")
async def login_telegram(data: TelegramLoginRequest):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise HTTPException(status_code=500, detail="Telegram bot token not configured")
    
    # Verify Telegram auth
    data_dict = data.dict()
    if not verify_telegram_auth(data_dict, bot_token):
        raise HTTPException(status_code=400, detail="Invalid Telegram authentication")
    
    # Check if user exists, or create new one
    user = await User.get_or_none(telegram_id=data.id)
    if not user:
        user = await User.create(
            telegram_id=data.id,
            full_name=f"{data.first_name} {data.last_name or ''}".strip(),
            role=UserRole.SEEKER  # Default role
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id), "role": str(user.role.value)})
    return {"access_token": access_token, "token_type": "bearer", "user": {
        "id": user.id,
        "full_name": user.full_name,
        "role": user.role
    }}

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.SEEKER

class LoginEmailRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register_user(data: RegisterRequest):
    if await User.get_or_none(email=data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = pwd_context.hash(data.password)
    user = await User.create(
        email=data.email,
        full_name=data.full_name,
        role=data.role,
        hashed_password=hashed
    )
    access_token = create_access_token(data={"sub": str(user.id), "role": str(user.role.value)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }

@router.post("/login/email")
async def login_email(data: LoginEmailRequest):
    user = await User.get_or_none(email=data.email)
    if not user or not user.hashed_password or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": str(user.id), "role": str(user.role.value)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }
