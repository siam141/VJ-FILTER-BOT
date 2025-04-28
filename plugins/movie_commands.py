from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.today_movies_db import get_today_movies, clear_today_movies  # Ensure clear_today_movies is implemented in your DB

POST_CHANNEL_ID = -1002589776901  # Put your actual post channel ID here
ADMIN_ID = 7862181538  # Replace with your actual admin ID

# Function to remove usernames like @username from movie title
def remove_usernames_from_title(title: str) -> str:
    import re
    return re.sub(r'@[\w_]+', '', title).strip()  # Remove '@' followed by word characters or underscores

# Function to format movie genres
def format_movie_genre(genre: str) -> str:
    if genre:
        return f"🎬 Genre: {genre}"
    return ""

# Command to list today's movies
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
        movie_title = remove_usernames_from_title(movie['title']).replace('.', ' ')  # Replace dots with spaces and remove usernames
        movie_genre = format_movie_genre(movie.get('genre', ''))
        movie_list += f"**{idx}.** 🎬 {movie_title}\n{movie_genre}\n\n"

    # Send the movie list as a reply
    await message.reply(
        f"**📅 Today's Movie List:**\n\n{movie_list}",
        quote=True
    )

# Command to post today's movies to a channel
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
        movie_title = remove_usernames_from_title(movie['title']).replace('.', ' ')  # Replace dots with spaces and remove usernames
        movie_genre = format_movie_genre(movie.get('genre', ''))
        movie_list += f"**{idx}.** 🎬 {movie_title}\n{movie_genre}\n\n"

    # Movie cover image URL (replace with your actual movie cover URL or path)
    movie_cover_url = "https://www.example.com/movie-cover.jpg"

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

    # Send the post message with inline buttons and movie cover image
    await client.send_message(
        POST_CHANNEL_ID,
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        caption="**🎬 Today's Movie Collection**",
        parse_mode="Markdown"
    )

# Clear list command to delete today's movie list (only admin can do this)
@Client.on_message(filters.command("clear_today_list") & filters.user(ADMIN_ID))
async def clear_today_movie_list(client, message):
    # Clear today's movie list in the database
    await clear_today_movies()  # Implement this function in your database module to clear the list

    # Notify the admin
    await message.reply("✅ Today's movie list has been cleared successfully!")