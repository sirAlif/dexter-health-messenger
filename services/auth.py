from passlib.context import CryptContext
from db.crud import get_user_by_username, create_user
from sqlalchemy.ext.asyncio import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, username: str, password: str):
        # Check if the user already exists using the database function
        existing_user = await get_user_by_username(self.db, username)
        if existing_user:
            raise Exception("Username already exists!")

        # Hash password and create user
        hashed_password = pwd_context.hash(password)
        new_user = await create_user(self.db, username, hashed_password)
        return {"message": "User created successfully!", "user_id": new_user.id}

    async def authenticate_user(self, username: str, password: str):
        user = await get_user_by_username(self.db, username)
        if user and pwd_context.verify(password, user.password_hash):
            return user
        raise Exception("Invalid credentials!")
