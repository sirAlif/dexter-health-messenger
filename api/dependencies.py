from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from services.auth import AuthService
from services.chat import ChatService
from services.openai import OpenAIService
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config.conf import Config

# Load environment variables
conf = Config()

# HTTPBearer is used to extract the token from the Authorization header
security = HTTPBearer()

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Dependency for the auth service
def get_user_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


# Dependency for the chat service
def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db)


# Dependency for the OpenAI service
def get_openai_service() -> OpenAIService:
    return OpenAIService()


# Functions used for handling JWT token
def create_access_token(data: dict):
    """
    Generate a JWT token for the provided data.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, conf.SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def validate_websocket_token(token: str):
    try:
        payload = jwt.decode(token, conf.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload["user_id"]
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """
    Extract and validate the token, returning the user ID.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, conf.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
