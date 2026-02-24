import motor.motor_asyncio
from typing import Optional
from pymongo import IndexModel, ASCENDING

from app.core.config import settings

client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
db = None


async def connect_db():
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.DATABASE_NAME]
    # ensure indexes
    await db.users.create_index([("email", ASCENDING)], unique=True)
    await db.chat_sessions.create_index([("user_id", ASCENDING)])
    await db.chat_sessions.create_index([("created_at", ASCENDING)])


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db
