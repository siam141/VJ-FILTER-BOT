from info import DB_URL, DB_NAME
import motor.motor_asyncio
from datetime import datetime, timedelta

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
db = client[DB_NAME]
todaymovies = db.todaymovies

async def save_today_movie(title: str):
    timestamp = datetime.utcnow()
    await todaymovies.insert_one({
        "title": title,
        "timestamp": timestamp
    })

async def get_today_movies():
    today = datetime.utcnow()
    twelve_hours_ago = today - timedelta(hours=12)
    movies = await todaymovies.find({
        "timestamp": {"$gte": twelve_hours_ago}
    }).to_list(length=100)
    return movies

async def clear_old_movies():
    twelve_hours_ago = datetime.utcnow() - timedelta(hours=12)
    await todaymovies.delete_many({
        "timestamp": {"$lt": twelve_hours_ago}
    })