import aiohttp
from info import TMDB_API_KEY

BASE_URL = "https://api.themoviedb.org/3"

async def search_movie(query):
    if not TMDB_API_KEY:
        raise ValueError("TMDB API Key is missing!")

    url = f"{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("results", [])
                else:
                    print(f"TMDB API error: {resp.status}")
                    return []
        except aiohttp.ClientError as e:
            print(f"HTTP Request failed: {e}")
            return []