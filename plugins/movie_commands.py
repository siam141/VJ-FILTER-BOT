from pyrogram import Client, filters
from database.today_movies_db import get_today_movies

POST_CHANNEL_ID = -1002589776901  # এখানে তোমার পোস্ট চ্যানেল ID বসাও

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("❌ আজকের কোনো মুভি পাওয়া যায়নি!")
        return

    movie_list = ""
    for index, movie in enumerate(movies, start=1):
        movie_list += f"**{index}.** 🎬 {movie['title']}\n"

    text = f"""
📅 **আজকের আপলোড মুভির তালিকা:**

{movie_list}

🕙 আপডেট: প্রতি ১২ ঘণ্টায় নতুন করে রিফ্রেশ হয়।
    """.strip()

    await message.reply(text)

@Client.on_message(filters.command("postlist"))
async def post_today_movies(client, message):
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("❌ আজকের কোনো মুভি নেই পোস্ট করার জন্য!")
        return

    movie_list = ""
    for index, movie in enumerate(movies, start=1):
        movie_list += f"**{index}.** 🎬 {movie['title']}\n"

    text = f"""
🌟 **আজকের মুভি কালেকশন:** 🌟

{movie_list}

🔗 সমস্ত মুভি একসাথে পেতে যুক্ত থাকুন!
📌 Powered by @YourBotUsername
    """.strip()

    await client.send_message(POST_CHANNEL_ID, text)