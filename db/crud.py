from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Message
from sqlalchemy import or_


# User-related database functions
async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User:
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, username: str, hashed_password: str) -> User:
    new_user = User(username=username, password_hash=hashed_password)
    db.add(new_user)
    await db.commit()
    return new_user


# Message-related database functions
async def get_messages_between_users(db: AsyncSession, user_id: int, contact_username: str):
    result = await db.execute(
        select(Message)
        .join(User, or_(Message.sender_id == User.id, Message.receiver_id == User.id))
        .filter(
            or_(
                (Message.sender_id == user_id) & (User.username == contact_username),
                (Message.receiver_id == user_id) & (User.username == contact_username),
            )
        )
        .order_by(Message.timestamp)
    )
    return result.scalars().all()


async def get_user_contacts(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User.username)
        .join(Message, or_(Message.sender_id == User.id, Message.receiver_id == User.id))
        .filter(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
        .filter(User.id != user_id)
        .distinct()
    )
    return result.scalars().all()


async def save_message(db: AsyncSession, sender_id: int, receiver_id: int, content: str) -> Message:
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(message)
    await db.commit()
    return message
