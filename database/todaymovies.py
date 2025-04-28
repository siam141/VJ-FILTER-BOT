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
    start = datetime(today.year, today.month, today.day)
    end = start + timedelta(days=1)
    movies = await todaymovies.find({
        "timestamp": {"$gte": start, "$lt": end}
    }).to_list(length=100)
    return movies