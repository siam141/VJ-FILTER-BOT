from pyrogram import Client, filters
from database.todaymovies import save_today_movie
from helper import get_clean_title

LOG_CHANNEL_ID = -1002589776901

@Client.on_message(filters.chat(LOG_CHANNEL_ID) & filters.video)
async def save_movie_to_db(client, message):
    title = message.caption
    if not title:
        title = get_clean_title(message.video.file_name)
    await save_today_movie(title)