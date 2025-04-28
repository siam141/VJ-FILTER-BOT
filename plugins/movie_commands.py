import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.today_movies_db import get_today_movies, clear_today_movies

POST_CHANNEL_ID = -1002589776901  # Put your actual post channel ID here
ADMIN_ID = 7862181538  # Replace with your actual admin ID

def remove_usernames_from_title(title: str) -> str:
    # Regular expression to match '@username' or '@some_text'
    return re.sub(r'@[\w_]+', '', title).strip()  # Remove '@' followed by word characters or underscores

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    # Fetch today's movies from your database
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("❌ No movies found for today!")
        return

    # Building movie list
    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)  # Remove username if any
        movie_list += f"**{idx}.** 🎬 {movie_title}\n\n"

    # Send the movie list as a reply
    await message.reply(
        f"**📅 Today's Movie List:**\n\n{movie_list}",
        quote=True
    )

@Client.on_message(filters.command("postlist"))
async def post_today_movies(client, message):
    # Fetch today's movies from your database
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("❌ No movies available to post today!")
        return

    # Build the movie list with buttons
    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)  # Remove username if any
        movie_list += f"**{idx}.** 🎬 {movie_title}\n\n"

    text = f"""
🎬 **Today's Movie Collection** 📅

{movie_list}

━━━━━━━━━━━━━━━

💡 **Click the buttons below to get the movie or search for it:**

👇👇👇

🎬 **Get Now**  
🔍 **Search Now**

━━━━━━━━━━━━━━━

📌 Powered by [YourBotUsername](https://t.me/YourBotUsername)

📣 For more updates, follow our [Channel](https://t.me/YourChannelLink)
"""

    # Inline buttons setup for action
    buttons = [
        [
            InlineKeyboardButton("Get Now", url="https://www.example.com/movie-link"),  # Replace with actual movie link
            InlineKeyboardButton("Search Now", url="https://www.example.com/search-now")  # Replace with actual search link
        ]
    ]

    # Send the post message with inline buttons
    await client.send_message(
        POST_CHANNEL_ID,
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command("clear_today_list") & filters.user(ADMIN_ID))
async def clear_today_movie_list(client, message):
    # Clear today's movie list in the database
    await clear_today_movies()  # This will now work after implementation
    
    # Notify the admin
    await message.reply("✅ Today's movie list has been cleared successfully!")