from db.crud import get_user_by_id, get_user_by_username, get_messages_between_users, get_user_contacts, save_message
from sqlalchemy.ext.asyncio import AsyncSession


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_message_to_user(self, data, connected_users):
        sender_id = data["sender_id"]
        receiver_username = data["contact"]
        message_content = data["content"]

        sender = await get_user_by_id(self.db, sender_id)
        if not sender:
            raise Exception(f"Sender with id {sender_id} not found.")

        receiver = await get_user_by_username(self.db, receiver_username)
        if not receiver:
            raise Exception(f"Receiver with username {receiver_username} not found.")

        receiver_id = receiver.id
        await save_message(self.db, sender_id, receiver_id, message_content)

        # Notify the receiver if they are connected
        if receiver_id in connected_users:
            await connected_users[receiver_id].send_json({"sender": sender.username, "content": message_content})

    async def is_valid_user_id(self, contact) -> bool:
        user = await get_user_by_username(self.db, contact)
        return user is not None

    async def get_user_conversation(self, user_id: int, contact_username: str):
        messages = await get_messages_between_users(self.db, user_id, contact_username)
        return messages if messages else None

    async def get_user_contacts(self, user_id: int):
        contacts = await get_user_contacts(self.db, user_id)
        return contacts
