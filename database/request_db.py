# database/request_db.py

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from info import DB_URL, DB_NAME

class RequestDatabase:
    def __init__(self):
        self.client = AsyncIOMotorClient(DB_URL)
        self.db = self.client[DB_NAME]
        self.requests = self.db.requests

    async def add_request(self, user_id: int, movie_name: str):
        data = {
            "user_id": user_id,
            "movie_name": movie_name,
            "requested_at": datetime.utcnow()
        }
        await self.requests.insert_one(data)

    async def get_all_requests(self):
        return await self.requests.find().to_list(length=None)

    async def delete_request(self, user_id: int, movie_name: str):
        await self.requests.delete_one({"user_id": user_id, "movie_name": movie_name})

    async def clear_requests(self):
        await self.requests.delete_many({})

    async def find_request(self, user_id: int):
        return await self.requests.find_one({"user_id": user_id})