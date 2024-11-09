from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.message_service import create_user, send_message, get_user_conversation
from db.database import get_db
from db.models import MessageResponse, UserCreate

router = APIRouter()


@router.post("/users/")
async def create_user_route(user: UserCreate, db: AsyncSession = Depends(get_db)):
    response = await create_user(db, user.username)
    if response.get("message") is not None:
        return response
    if response.get('error') is not None:
        raise HTTPException(status_code=400, detail=response['error'])


@router.post("/messages/")
async def create_message(message: MessageResponse, db: AsyncSession = Depends(get_db)):
    return await send_message(db, message.sender_id, message.receiver_id, message.content)


@router.get("/messages/{user_id}")
async def get_user_messages(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_conversation(db, user_id)
