from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.today_movies_db import get_today_movies, clear_today_movies  # Make sure this is implemented in your DB

POST_CHANNEL_ID = -1002589776901  # Put your actual post channel ID here
ADMIN_ID = 7862181538  # Replace with your actual admin ID

# Fetch today's movies and send the list to the user
@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    # Fetch today's movies from your database
    movies = await get_today_movies()

    if not movies:
        await message.reply("❌ No movies found for today!")
        return

    # Building the movie list
    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title'].replace('.', ' ')  # Replace dots with spaces
        movie_list += f"**{idx}.** 🎬 {movie_title}\n\n"

    # Send the movie list as a reply
    await message.reply(
        f"**📅 Today's Movie List:**\n\n{movie_list}",
        quote=True
    )


# Post today's movies in the channel with buttons
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
        movie_title = movie['title'].replace('.', ' ')  # Replace dots with spaces
        movie_list += f"**{idx}.** 🎬 {movie_title}\n\n"

    # The post message text
    text = f"""
**🎬 Today's Movie Collection:**

{movie_list}

━━━━━━━━━━━━━━━
📌 Powered by @YourBotUsername

🌟 Enjoy the Movies, and Stay Tuned for More!
"""

    # Inline buttons setup for action
    buttons = [
        [
            InlineKeyboardButton("Get Now", url="https://www.example.com/movie-link")  # Replace with actual movie link
        ],
        [
            InlineKeyboardButton("See More Movies", url="https://www.example.com/movies")  # Link to see more movies
        ]
    ]

    try:
        # Send the post message with inline buttons
        await client.send_message(
            POST_CHANNEL_ID,
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
            caption="**🎬 Today's Movie Collection**",
            parse_mode="Markdown"
        )
        # Notify in the chat after posting
        await message.reply("✅ Today's movies have been posted successfully!")

    except Exception as e:
        # If there's an error, send the error message
        await message.reply(f"❌ Failed to post: {e}")


# Clear today's movie list (admin only)
@Client.on_message(filters.command("clear_today_list") & filters.user(ADMIN_ID))
async def clear_today_movie_list(client, message):
    # Clear today's movie list in the database
    await clear_today_movies()  # This will now work after implementation

    # Notify the admin
    await message.reply("✅ Today's movie list has been cleared successfully!")


# Clear list command to delete today's movie list (only admin can do this)
@Client.on_message(filters.command("clear_list") & filters.user(ADMIN_ID))
async def clear_movie_list(client, message):
    # Clear the movie list in your database
    result = await clear_today_movies()  # Implement this function in your database module to clear the list

    if result:
        await message.reply("✅ Today's movie list has been cleared successfully!")
    else:
        await message.reply("❌ Failed to clear the movie list. Please try again.")