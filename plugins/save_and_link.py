from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS, BOT_USERNAME
from database.movies import add_movie_entry, get_movie_by_id

# ✅ /savemovie (রিপ্লাই করা মুভি সেভ করে ডাটাবেজে)
@Client.on_message(filters.command("savemovie") & filters.user(ADMINS) & filters.reply)
async def save_movie_handler(client, message: Message):
    reply = message.reply_to_message
    file_name = reply.caption or "Untitled Movie"
    await add_movie_entry(reply.id, reply.chat.id, file_name)
    await message.reply_text("✅ মুভি সফলভাবে ডাটাবেজে সেভ হয়েছে।")

# ✅ /getlink (মুভির ইউনিক লিংক তৈরি করে)
@Client.on_message(filters.command("getlink") & filters.user(ADMINS))
async def get_link_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /getlink <message_id>")
    
    msg_id = int(message.command[1])
    movie = await get_movie_by_id(msg_id)
    
    if not movie:
        return await message.reply("❌ ডাটাবেজে মুভিটি খুঁজে পাওয়া যায়নি।")
    
    link = f"https://t.me/{BOT_USERNAME}?start=movie_{msg_id}"
    await message.reply_text(f"🎬 **{movie['file_name']}**\n\n🔗 শেয়ার লিংক:\n{link}")