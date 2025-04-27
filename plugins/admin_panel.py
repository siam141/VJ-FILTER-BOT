from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp

# তোমার TMDb API Key
TMDB_API = "c3443ed2f96cd615e3badf6b68c8a689"

@Client.on_message(filters.command("admins"))
async def start(client, message):
    buttons = [
        [InlineKeyboardButton("Trending Movies", callback_data="trending_movies")]
    ]
    await message.reply_text(
        "Welcome!\n\nSearch your favorite movies or check trending movies!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("trending_movies"))
async def trending_movies_handler(client, query):
    await query.answer()
    trending_url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(trending_url) as response:
                data = await response.json()
                movies = data.get("results", [])[:10]  # প্রথম ১০টি ট্রেন্ডিং মুভি দেখাবে
                if not movies:
                    await query.message.edit("No trending movies found!")
                    return
                text = "**Trending Movies:**\n\n"
                for movie in movies:
                    title = movie.get("title")
                    release = movie.get("release_date", "N/A")
                    text += f"**{title}** ({release})\n"
                await query.message.edit(text)
    except Exception as e:
        await query.message.edit(f"Error fetching trending movies.\n\n{e}")