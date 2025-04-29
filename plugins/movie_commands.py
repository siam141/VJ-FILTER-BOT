import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery
from database.today_movies_db import get_today_movies, clear_today_movies

POST_CHANNEL_ID = -1002507577541  # Your post channel ID
ADMIN_ID = 7862181538  # Your admin ID
POST_IMAGE_URL = "https://i.ibb.co/21RKmKDG/file-1485.jpg"  # Image URL to post
MOVIES_PER_PAGE = 5

def remove_usernames_from_title(title: str) -> str:
    return re.sub(r'@[\w_]+', '', title).strip()

def replace_underscore_with_space(title: str) -> str:
    return title.replace("_", " ")

def create_movie_list(movies, page=0):
    start = page * MOVIES_PER_PAGE
    end = start + MOVIES_PER_PAGE
    movie_list = ""
    for idx, movie in enumerate(movies[start:end], start=start+1):
        movie_title = remove_usernames_from_title(movie['title'])
        movie_title = replace_underscore_with_space(movie_title)
        movie_list += f"**{idx}.** 🎯 {movie_title}\n\n"
    return movie_list

def create_buttons(total_movies, page):
    buttons = []
    navigation_buttons = []

    max_page = (total_movies - 1) // MOVIES_PER_PAGE

    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{page}"))
    if page < max_page:
        navigation_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"next_{page}"))
    
    if navigation_buttons:
        buttons.append(navigation_buttons)

    buttons.append([InlineKeyboardButton("🎬 Get Now", url="https://t.me/MovieDownload6G_bot")])

    return InlineKeyboardMarkup(buttons)

@Client.on_message(filters.command("postlist") & filters.user(ADMIN_ID))
async def post_today_movies(client, message):
    movies = await get_today_movies()

    if not movies:
        await message.reply("🚫 No movies available to post today!")
        return

    movie_list = create_movie_list(movies, page=0)
    buttons = create_buttons(len(movies), page=0)

    sent = await client.send_photo(
        POST_CHANNEL_ID,
        photo=POST_IMAGE_URL,
        caption=f"**🎉 Today's Movie List:**\n\n{movie_list}",
        reply_markup=buttons
    )

    await message.reply("✅ Successfully posted today's movie list in the channel!")

@Client.on_callback_query(filters.regex(r'^(next|prev)_\d+$'))
async def paginate_movies(client, query: CallbackQuery):
    action, current_page = query.data.split("_")
    current_page = int(current_page)
    
    movies = await get_today_movies()
    total_movies = len(movies)

    if action == "next":
        page = current_page + 1
    else:
        page = current_page - 1

    movie_list = create_movie_list(movies, page)
    buttons = create_buttons(total_movies, page)

    try:
        await query.message.edit_caption(
            caption=f"**🎉 Today's Movie List:**\n\n{movie_list}",
            reply_markup=buttons
        )
    except Exception as e:
        await query.answer("Something went wrong!", show_alert=True)

@Client.on_message(filters.command("clear_today_list") & filters.user(ADMIN_ID))
async def clear_today_movie_list(client, message):
    await clear_today_movies()
    await message.reply("✅ Today's movie list has been cleared successfully!")