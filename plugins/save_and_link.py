from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.file_store_db import save_file, get_file_by_key
import random, string

def generate_key(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@Client.on_message(filters.command("link") & filters.reply)
async def single_link_handler(bot, message: Message):
    reply = message.reply_to_message
    if not (reply.document or reply.video or reply.audio):
        return await message.reply("Please reply to a valid media file.")

    key = generate_key()
    await save_file(key, reply, forward_restricted=False)

    link = f"https://t.me/{bot.username}?start={key}"
    await message.reply(f"Here is your sharable link:\n`{link}`")

@Client.on_message(filters.command("plink") & filters.reply)
async def single_plink_handler(bot, message: Message):
    reply = message.reply_to_message
    if not (reply.document or reply.video or reply.audio):
        return await message.reply("Please reply to a valid media file.")

    key = generate_key()
    await save_file(key, reply, forward_restricted=True)

    link = f"https://t.me/{bot.username}?start={key}"
    await message.reply(f"Here is your **Protected Link**:\n`{link}`")

@Client.on_message(filters.command("start") & filters.private)
async def serve_stored_file(bot, message: Message):
    args = message.text.split()
    if len(args) == 2:
        key = args[1]
        data = await get_file_by_key(key)
        if not data:
            return await message.reply("Invalid or expired file link.")
        
        if data.get("forward_restricted"):
            await bot.forward_messages(
                chat_id=message.chat.id,
                from_chat_id=data['chat_id'],
                message_ids=data['message_id'],
                disable_notification=True
            )
        else:
            await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=data['chat_id'],
                message_id=data['message_id']
            )