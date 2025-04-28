from pyrogram import Client, filters
from database.todaymovies import save_today_movie

LOG_CHANNEL_ID = -1002589776901

@Client.on_message(filters.chat(LOG_CHANNEL_ID) & filters.video)
async def save_movie_to_db(client, message):
    title = message.caption if message.caption else "No Title"
    await save_today_movie(title)