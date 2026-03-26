from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import hashlib
import hmac

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_telegram_auth(data: dict, bot_token: str) -> bool:
    sha256_hash = hashlib.sha256(bot_token.encode()).digest()
    hash_to_check = data.pop('hash', None)
    if not hash_to_check:
        return False
    
    data_check_list = []
    for key, value in sorted(data.items()):
        data_check_list.append(f"{key}={value}")
    data_check_string = "\n".join(data_check_list)
    
    calculated_hash = hmac.new(sha256_hash, data_check_string.encode(), hashlib.sha256).hexdigest()
    return calculated_hash == hash_to_check

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
