from pyrogram import Client, filters
from database.today_movies_db import get_today_movies
import re

POST_CHANNEL_ID = -1002589776901  # এখানে তোমার পোস্ট চ্যানেল ID বসাও

# ভিডিও ফরম্যাট এক্সটেনশন বাদ দেয়া এবং ডট সরানো
def clean_movie_title(movie_title):
    cleaned_title = re.sub(r'\.(mp4|mkv|avi|mov|flv|webm)', '', movie_title, flags=re.IGNORECASE)  # এক্সটেনশন বাদ দেয়া
    cleaned_title = cleaned_title.replace('.', ' ')  # ডট (.) সরানো
    return cleaned_title

# আজকের মুভির তালিকা দেখানো
@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("❌ আজকের কোনো মুভি পাওয়া যায়নি!")
        return

    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        cleaned_title = clean_movie_title(movie['title'])  # এক্সটেনশন বাদ দেওয়া এবং ডট সরানো
        movie_list += f"**🔹 {idx}.** 🎬 {cleaned_title}\n\n"

    await message.reply(
        f"**📅 আজকের আপলোড মুভির তালিকা:**\n\n{movie_list}",
        quote=True
    )

# আজকের মুভি পোস্ট করা
@Client.on_message(filters.command("postlist"))
async def post_today_movies(client, message):
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("❌ আজকের কোনো মুভি নেই পোস্ট করার জন্য!")
        return

    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        cleaned_title = clean_movie_title(movie['title'])  # এক্সটেনশন বাদ দেওয়া এবং ডট সরানো
        movie_list += f"🎬 **{cleaned_title}**\n"
        movie_list += f"🔹 **{idx}.** {cleaned_title}\n\n"

    text = f"""
**🎬 আজকের মুভি কালেকশন:**

{movie_list}

━━━━━━━━━━━━━━━
📌 Powered by @YourBotUsername

🔹 **আমাদের সাথে যুক্ত থাকতে**: @YourChannelUsername
"""

    # এখানে বাটন যুক্ত করা হচ্ছে
    buttons = [
        [
            ("🎬 Get Now", "https://t.me/YourBotUsername?start=movie1"),  # উদাহরণ লিঙ্ক
            ("🔍 Search Now", "https://www.google.com/search?q=MovieName")  # সার্চ লিঙ্ক
        ]
    ]

    # মুভির নাম কপি করার জন্য ইনলাইন বাটন
    copy_button = [
        [
            ("📋 Copy Title", "copy://{cleaned_title}")  # কপি করার জন্য লিঙ্ক (এটা প্রকৃত কপি লিঙ্ক নয়, উদাহরণ হিসেবে)
        ]
    ]

    await client.send_message(POST_CHANNEL_ID, text, reply_markup=buttons)
    await client.send_message(POST_CHANNEL_ID, text, reply_markup=copy_button)