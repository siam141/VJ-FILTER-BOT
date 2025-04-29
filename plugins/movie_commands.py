import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.today_movies_db import get_today_movies, clear_today_movies

POST_CHANNEL_ID = -1002507577541  # Your post channel ID
ADMIN_ID = 7862181538  # Your admin ID
POST_IMAGE_URL = "https://i.ibb.co/21RKmKDG/file-1485.jpg"  # Image URL to post

def remove_usernames_from_title(title: str) -> str:
    # Remove @username from title
    return re.sub(r'@[\w_]+', '', title).strip()

def replace_underscore_with_space(title: str) -> str:
    # Replace underscores with spaces
    return title.replace("_", " ")

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    movies = await get_today_movies()

    if not movies:
        await message.reply("🚫 No movies found for today!")
        return

    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)
        movie_title = replace_underscore_with_space(movie_title)

        movie_list += f"**{idx}.** 🎯 `{movie_title}`\n\n"  # Added Mono font style

    await message.reply(
        f"**🎉 Today's Movie List:**\n\n{movie_list}",
        quote=True
    )

@Client.on_message(filters.command("postlist") & filters.user(ADMIN_ID))
async def post_today_movies(client, message):
    movies = await get_today_movies()

    if not movies:
        await message.reply("🚫 No movies available to post today!")
        return

    movie_list = ""
    buttons = []  # To hold the buttons for inline keyboard
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)
        movie_title = replace_underscore_with_space(movie_title)

        # Creating the inline button for each movie title
        button = InlineKeyboardButton(
            text=f"🎯 `{movie_title}`",  # Added Mono font style to button text
            callback_data=f"copy_{movie_title}"  # Attach movie title in callback_data
        )
        buttons.append([button])  # Add button to buttons list

        movie_list += f"**{idx}.** `{movie_title}`\n"  # Added Mono font style

    # First send the message in channel with photo and Mono font style for movie titles
    await client.send_photo(
        POST_CHANNEL_ID,
        photo=POST_IMAGE_URL,
        caption=f"**🎉 Today's Movie List:**\n\n{movie_list}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    # Notify admin
    await message.reply("✅ Successfully posted today's movie list in the channel!")

@Client.on_message(filters.command("clear_today_list") & filters.user(ADMIN_ID))
async def clear_today_movie_list(client, message):
    await clear_today_movies()
    await message.reply("✅ Today's movie list has been cleared successfully!")