# autoclear.py

import asyncio
from database.today_movies_db import clear_all_movies

async def auto_clear_loop():
    while True:
        await asyncio.sleep(43200)  # 12 ঘন্টা = 43200 সেকেন্ড
        await clear_all_movies()