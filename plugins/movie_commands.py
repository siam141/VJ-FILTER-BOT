# plugins/movie_commands.py

from pyrogram import Client, filters
from database.today_movies_db import get_today_movies
from datetime import datetime

POST_CHANNEL_ID = -1001234567890  # এখানে তোমার পোস্ট করার চ্যানেলের আইডি বসাও

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("আজকের কোনো মুভি পাওয়া যায়নি!")
        return

    movie_list = "\n".join(f"• {m['title']}" for m in movies)
    await message.reply(f"**আজকের আপলোড মুভির তালিকা:**\n\n{movie_list}")

@Client.on_message(filters.command("postlist"))
async def post_today_movies(client, message):
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("আজকের কোনো মুভি নেই পোস্ট করার জন্য!")
        return

    movie_list = "\n".join(f"🎬 {m['title']}" for m in movies)
    text = f"**আজকের মুভি কালেকশন:**\n\n{movie_list}\n\n📌 Powered by @YourBotUsername"
    await client.send_message(POST_CHANNEL_ID, text)