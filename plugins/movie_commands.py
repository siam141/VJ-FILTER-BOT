import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto
from database.today_movies_db import get_today_movies, clear_today_movies

POST_CHANNEL_ID = -1002507577541  # Your post channel ID
ADMIN_ID = 7862181538  # Your admin ID
POST_IMAGE_URL = "https://i.ibb.co/21RKmKDG/file-1485.jpg"  # Image URL to post
MOVIES_PER_PAGE = 5  # প্রতি পেজে কত মুভি দেখাবো

# ======== Helper functions ==========
def remove_usernames_from_title(title: str) -> str:
    return re.sub(r'@[\w_]+', '', title).strip()

def replace_dot_and_underscore_with_space(title: str) -> str:
    title = title.replace("_", " ")
    title = title.replace(".", " ")
    return title

def remove_extra_words_from_title(title: str) -> str:
    patterns = [
        r"\bWEB[-_.]?DL\b", r"\bWEBRip\b", r"\bHDRip\b", r"\bBluRay\b",
        r"\b1080p\b", r"\b720p\b", r"\b480p\b", r"\.mkv", r"\.mp4", r"\.avi",
        r".*?", r".*?"
    ]
    for pattern in patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    return title.strip()

def clean_title(title: str) -> str:
    title = remove_usernames_from_title(title)
    title = replace_dot_and_underscore_with_space(title)
    title = remove_extra_words_from_title(title)
    title = re.sub(' +', ' ', title)
    return title.strip()

def generate_movie_list(movies, page=0):
    start = page * MOVIES_PER_PAGE
    end = start + MOVIES_PER_PAGE
    movie_list = ""
    for idx, movie in enumerate(movies[start:end], start=start+1):
        movie_title = clean_title(movie['title'])
        movie_list += f"`{idx}. {movie_title}`\n\n"
    return movie_list

def generate_buttons(movies, page=0):
    total_pages = (len(movies) - 1) // MOVIES_PER_PAGE
    buttons = []

    # Prev / Next Button
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"next_{page+1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    # Get Now Button
    buttons.append([
        InlineKeyboardButton("🎬 Get Now", url="https://t.me/MovieDownload6G_bot"),
        InlineKeyboardButton("🎯 Join Now", url="https://t.me/Movie_channel8")
    ])
    return InlineKeyboardMarkup(buttons)

# ========== Commands ==========

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    movies = await get_today_movies()

    if not movies:
        await message.reply("🚫 No movies found for today!")
        return

    movie_list = generate_movie_list(movies)

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

    movie_list = generate_movie_list(movies)
    buttons = generate_buttons(movies)

    sent_message = await client.send_photo(
        POST_CHANNEL_ID,
        photo=POST_IMAGE_URL,
        caption=f"**🎉 Today's Movie List:**\n\n{movie_list}",
        reply_markup=buttons
    )

    # Save posted message ID and movies for navigation
    client.posted_message_id = sent_message.message_id
    client.posted_movies = movies

    await message.reply("✅ Successfully posted today's movie list in the channel!")

@Client.on_message(filters.command("clear_today_list") & filters.user(ADMIN_ID))
async def clear_today_movie_list(client, message):
    await clear_today_movies()
    await message.reply("✅ Today's movie list has been cleared successfully!")

# ========== Callback Queries ==========

@Client.on_callback_query(filters.regex(r'^(next|prev)_(\d+)$'))
async def paginate_movies(client, callback_query: CallbackQuery):
    action, page = callback_query.data.split("_")
    page = int(page)

    movies = getattr(client, 'posted_movies', None)
    message_id = getattr(client, 'posted_message_id', None)

    if not movies or message_id is None:
        await callback_query.answer("No posted movie list found!", show_alert=True)
        return

    movie_list = generate_movie_list(movies, page)
    buttons = generate_buttons(movies, page)

    try:
        await client.edit_message_caption(
            chat_id=POST_CHANNEL_ID,
            message_id=message_id,
            caption=f"**🎉 Today's Movie List:**\n\n{movie_list}",
            reply_markup=buttons
        )
        await callback_query.answer()
    except Exception as e:
        await callback_query.answer(str(e), show_alert=True)