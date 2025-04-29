from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI

client = AsyncIOMotorClient(DATABASE_URI)
db = client["MovieBot"]
movie_col = db["movies"]

# ✅ মুভি সেভ করা
async def add_movie_entry(message_id: int, channel_id: int, file_name: str):
    await movie_col.update_one(
        {"message_id": message_id},
        {"$set": {
            "message_id": message_id,
            "channel_id": channel_id,
            "file_name": file_name
        }},
        upsert=True
    )

# ✅ মুভি রিটার্ন করা
async def get_movie_by_id(message_id: int):
    return await movie_col.find_one({"message_id": message_id})