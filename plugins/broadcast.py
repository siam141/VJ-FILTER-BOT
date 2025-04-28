# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import datetime, time, asyncio
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, broadcast_messages_group
        
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message):
    b_msg = await bot.ask(chat_id = message.from_user.id, text = "Now Send Me Your Broadcast Message")
    try:
        users = await db.get_all_users()
        sts = await message.reply_text('Broadcasting your messages...')
        start_time = time.time()
        total_users = await db.total_users_count()
        done = 0
        blocked = 0
        deleted = 0
        failed = 0
        success = 0
        async for user in users:
            if 'id' in user:
                pti, sh = await broadcast_messages(int(user['id']), b_msg)
                if pti:
                    success += 1
                elif pti == False:
                    if sh == "Blocked":
                        blocked += 1
                    elif sh == "Deleted":
                        deleted += 1
                    elif sh == "Error":
                        failed += 1
                done += 1
                if not done % 20:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
            else:
                # Handle the case where 'id' key is missing in the user dictionary 
                done += 1
                failed += 1
                if not done % 20:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
    
        time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
        await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
    except Exception as e:
        print(f"error: {e}")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS))
async def broadcast_group(bot, message):
    b_msg = await bot.ask(chat_id = message.from_user.id, text = "Now Send Me Your Broadcast Message")
    groups = await db.get_all_chats()
    sts = await message.reply_text(
        text='Broadcasting your messages To Groups...'
    )
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done = 0
    failed = 0

    success = 0
    async for group in groups:
        pti, sh = await broadcast_messages_group(int(group['id']), b_msg)
        if pti:
            success += 1
        elif sh == "Error":
                failed += 1
        done += 1
        if not done % 20:
            await sts.edit(f"Broadcast in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")
        










# plugins/request.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.request_db import RequestDatabase
from utils.formatters import format_request
from info import ADMINS, LOG_CHANNEL

db = RequestDatabase()

# User Command - /requestmovie
@Client.on_message(filters.command("requestmovie") & filters.private)
async def request_movie(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❗ Usage: `/requestmovie Movie Name`")
    
    movie_name = message.text.split(None, 1)[1]
    existing = await db.find_request(message.from_user.id)
    
    if existing:
        return await message.reply_text("❗ You have already requested a movie. Please wait until it is processed.")
    
    await db.add_request(message.from_user.id, movie_name)
    await message.reply_text(f"✅ Your request for `{movie_name}` has been submitted successfully!\nYou will be notified once it becomes available.")

    try:
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=format_request(movie_name, message.from_user.first_name, message.from_user.id, datetime.utcnow()),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{message.from_user.id}_{movie_name}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{message.from_user.id}_{movie_name}")
                ]
            ])
        )
    except Exception as e:
        print(f"Error while sending to admin: {e}")

# User Command - /cancelrequest
@Client.on_message(filters.command("cancelrequest") & filters.private)
async def cancel_request(client, message):
    request = await db.find_request(message.from_user.id)
    if not request:
        return await message.reply_text("❗ You have no active request to cancel.")
    
    await db.delete_request(message.from_user.id, request['movie_name'])
    await message.reply_text("✅ Your request has been successfully cancelled.")

# Admin Command - /requestlist
@Client.on_message(filters.command("requestlist") & filters.user(ADMINS))
async def request_list(client, message):
    requests = await db.get_all_requests()
    if not requests:
        return await message.reply_text("✅ No pending requests.")
    
    text = "**📃 Pending Movie Requests:**\n\n"
    for req in requests:
        time = req['requested_at'].strftime("%d-%m-%Y %I:%M %p")
        text += f"🎬 `{req['movie_name']}` | 🆔 `{req['user_id']}` | 🕰️ {time}\n"
    
    await message.reply_text(text)

# Admin Command - /clearrequests
@Client.on_message(filters.command("clearrequests") & filters.user(ADMINS))
async def clear_all_requests(client, message):
    await db.clear_requests()
    await message.reply_text("✅ All movie requests have been cleared successfully.")

# Callback Query Handler (Approve/Reject)
@Client.on_callback_query(filters.regex("^(approve|reject)_"))
async def handle_request_decision(client, callback_query):
    action, user_id, movie_name = callback_query.data.split("_", 2)
    user_id = int(user_id)

    if action == "approve":
        text = f"✅ Your movie request for `{movie_name}` has been accepted and it will be uploaded shortly!"
    else:
        text = f"❌ Sorry, your request for `{movie_name}` has been rejected."

    try:
        await client.send_message(chat_id=user_id, text=text)
        await db.delete_request(user_id, movie_name)
        await callback_query.message.edit_text(f"✅ Successfully processed the request for `{movie_name}`.")
    except Exception as e:
        await callback_query.message.edit_text(f"⚠️ Failed to process request: {e}")
