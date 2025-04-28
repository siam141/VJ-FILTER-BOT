# plugins/movie_bot.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.today_movies_db import get_today_movies
from utils import generate_unique_movie_link

POST_CHANNEL_ID = -1002589776901  # তোমার চ্যানেল আইডি (সঠিকভাবে বসাবে)

def remove_usernames_from_title(title: str) -> str:
    """Remove @usernames from the title."""
    words = title.split()
    cleaned_words = [word for word in words if not word.startswith("@")]
    return " ".join(cleaned_words)

def replace_underscore_with_space(title: str) -> str:
    """Replace underscores with spaces."""
    return title.replace("_", " ")

@Client.on_message(filters.command("postlist"))
async def post_today_movies(client, message):
    """Post today's movies with shareable links to a channel."""
    movies = await get_today_movies()

    if not movies:
        await message.reply("❌ আজকের জন্য কোনো মুভি পাওয়া যায়নি!")
        return

    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)
        movie_title = replace_underscore_with_space(movie_title)

        movie_link = movie.get('movie_link', '')  # ডাটাবেস থেকে লিঙ্ক

        movie_list += f"**{idx}.** [🎬 {movie_title}]({movie_link})\n\n"

    buttons = [
        [
            InlineKeyboardButton("Get Now", url="https://www.example.com/movie-link"),  # চেইঞ্জ করে নিজের লিঙ্ক বসাবে
            InlineKeyboardButton("Search Now", url="https://www.example.com/search-now")  # চেইঞ্জ করে নিজের লিঙ্ক বসাবে
        ]
    ]

    await client.send_message(
        POST_CHANNEL_ID,
        movie_list,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    """List today's movies without links."""
    movies = await get_today_movies()

    if not movies:
        await message.reply("❌ আজকের জন্য কোনো মুভি পাওয়া যায়নি!")
        return

    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)
        movie_title = replace_underscore_with_space(movie_title)

        movie_list += f"**{idx}.** {movie_title}\n\n"

    await message.reply(
        f"**📅 আজকের মুভি লিস্ট:**\n\n{movie_list}",
        disable_web_page_preview=True,
        quote=True
    )