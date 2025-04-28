# database/today_movies_db.py

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from info import DB_URL, DB_NAME

client = AsyncIOMotorClient(DB_URL)
db = client[DB_NAME]
movie_list_col = db.today_movie_list

async def save_movie(title: str):
    now = datetime.utcnow()
    twelve_hours_ago = now - timedelta(hours=12)

    # Check if the same movie was saved within 12 hours
    existing = await movie_list_col.find_one({
        "title": title,
        "time": {"$gte": twelve_hours_ago}
    })

    if not existing:
        await movie_list_col.insert_one({
            "title": title,
            "time": now
        })

async def get_today_movies():
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)
    movies = await movie_list_col.find({"time": {"$gte": yesterday}}).to_list(length=100)
    return movies

async def clear_all_movies():
    await movie_list_col.delete_many({})