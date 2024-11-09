from db import models

from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from sqlalchemy.future import select


async def create_user(db: AsyncSession, username: str):
    # Check if username already exists
    async with db.begin():
        existing_user = await db.execute(select(User).filter(User.username == username))
        existing_user = existing_user.scalar_one_or_none()
        if existing_user:
            return {"error": "Username already exists"}

        new_user = User(username=username)
        db.add(new_user)
        await db.commit()
        return {"message": "User created successfully"}


async def send_message(db: AsyncSession, sender_id: int, receiver_id: int, content: str):
    """
    Creates a new message in the database.
    """
    new_message = models.Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(new_message)
    await db.commit()  # Commit the transaction
    return {"message": "Message sent successfully"}


async def get_user_conversation(db: AsyncSession, user_id: int):
    """
    Retrieves all messages for a user, either sent or received.
    """
    # Use async query with select
    result = await db.execute(
        select(models.Message).filter(
            (models.Message.sender_id == user_id) | (models.Message.receiver_id == user_id)
        ).order_by(models.Message.timestamp)
    )
    # Fetch the results asynchronously
    messages = result.scalars().all()  # .scalars() gives the model objects directly
    return messages
