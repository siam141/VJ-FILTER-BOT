from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp

TMDB_API = "c3443ed2f96cd615e3badf6b68c8a689"

@Client.on_message(filters.command("start"))
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
                movies = data.get("results", [])[:10]
                if not movies:
                    await query.message.edit("No trending movies found!")
                    return
                buttons = []
                for movie in movies:
                    movie_id = movie.get("id")
                    title = movie.get("title", "No Title")
                    buttons.append(
                        [InlineKeyboardButton(f"{title}", callback_data=f"movie_{movie_id}")]
                    )
                await query.message.edit(
                    "**Trending Movies:**",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
    except Exception as e:
        await query.message.edit(f"Error fetching trending movies.\n\n{e}")

@Client.on_callback_query(filters.regex(r"movie_(\d+)"))
async def movie_detail_handler(client, query):
    movie_id = query.data.split("_")[1]
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(movie_url) as response:
                movie = await response.json()
                title = movie.get("title", "No Title")
                overview = movie.get("overview", "No Overview Available.")
                release = movie.get("release_date", "N/A")
                rating = movie.get("vote_average", "N/A")
                text = f"**{title}**\n\n**Release Date:** {release}\n**Rating:** {rating}\n\n**Overview:**\n{overview}"
                await query.message.edit(text)
    except Exception as e:
        await query.message.edit(f"Error fetching movie details.\n\n{e}")