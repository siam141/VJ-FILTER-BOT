from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.getenv("DB_URL"))
db = client["file_store"]
collection = db["files"]

async def save_file(key, msg, forward_restricted=False):
    data = {
        "key": key,
        "chat_id": msg.chat.id,
        "message_id": msg.message_id,
        "forward_restricted": forward_restricted
    }
    await collection.insert_one(data)

async def get_file_by_key(key):
    return await collection.find_one({"key": key})