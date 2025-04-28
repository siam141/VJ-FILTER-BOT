from motor.motor_asyncio import AsyncIOMotorClient
import time
from info import DB_URL, DB_NAME  # info.py থেকে import নিতে হবে

client = AsyncIOMotorClient(DB_URL)
db = client[DB_NAME]
col = db.postlist

async def save_post(file_id, title):
    timestamp = int(time.time())
    await col.insert_one({"file_id": file_id, "title": title, "timestamp": timestamp})

async def get_today_posts():
    current_time = int(time.time())
    twelve_hours_ago = current_time - 12 * 60 * 60  # 12 ঘন্টা আগে
    posts = await col.find({"timestamp": {"$gte": twelve_hours_ago}}).to_list(length=1000)
    return posts

async def clear_old_posts():
    current_time = int(time.time())
    twelve_hours_ago = current_time - 12 * 60 * 60
    await col.delete_many({"timestamp": {"$lt": twelve_hours_ago}})