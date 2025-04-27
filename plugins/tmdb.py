import aiohttp
import os

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")  # তোমার TMDb API Key লাগবে

BASE_URL = "https://api.themoviedb.org/3"

async def search_movie(query):
    url = f"{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("results", [])
            return []