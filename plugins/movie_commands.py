from pyrogram import Client, filters
from database.today_movies_db import get_today_movies
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

POST_CHANNEL_ID = -1002589776901  # আপনার চ্যানেল আইডি এখানে বসিয়েছি

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("❌ আজকের কোনো মুভি পাওয়া যায়নি!")
        return

    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_list += f"**{idx}.** 🎬 {movie['title']}\n\n"

    await message.reply(
        f"**📅 আজকের আপলোড মুভির তালিকা:**\n\n{movie_list}",
        quote=True
    )

@Client.on_message(filters.command("postlist"))
async def post_today_movies(client, message):
    movies = await get_today_movies()
    
    if not movies:
        await message.reply("❌ আজকের কোনো মুভি নেই পোস্ট করার জন্য!")
        return

    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title'].replace('.', ' ')  # ডটগুলি মুছে ফেলা হচ্ছে
        movie_list += f"✅ **{idx}.** {movie_title}\n"

    text = f"""
**🎬 আজকের মুভি কালেকশন:**

{movie_list}

━━━━━━━━━━━━━━━
📌 Powered by @YourBotUsername

💡 বাটন ক্লিক করে আজকের মুভি সহজে পেয়ে যান!

"""

    # Inline button setup
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 Get Now", callback_data="post_movie")],  # Callback data for the button
        [InlineKeyboardButton("🔍 Search Now", url="https://example.com/search")]  # এখানে সার্চ লিঙ্ক দিন
    ])

    # Send message with buttons
    await client.send_message(POST_CHANNEL_ID, text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("post_movie"))
async def post_movie_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id  # Get the user ID of the person who clicked the button
    await callback_query.answer("🎬 আপনি পোস্ট দেওয়ার জন্য প্রস্তুত! এখানে আপনার মুভি পোস্ট করুন।")
    # আপনি চাইলে এখানে আরও কাস্টমাইজ করা মেসেজও পাঠাতে পারেন
    await client.send_message(user_id, "📝 আপনি এখন পোস্ট করতে পারবেন! পোস্ট দিন 👇👇👇")