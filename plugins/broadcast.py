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
        













from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.gfilters_mdb import add_movie_request, delete_movie_request, get_all_requests, clear_all_requests
from helper.tmdb import search_movie, get_movie_details
from datetime import datetime
from info import ADMIN_IDS, LOG_CHANNEL, MAX_REQUESTS_PER_DAY, REQUEST_EXPIRE_DAYS

# ইউজার রিকোয়েস্ট হ্যান্ডলার
@Client.on_message(filters.command("requestbots") & filters.private)
async def handle_request(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/requestbots Movie Name`", quote=True)

    movie_name = " ".join(message.command[1:])
    user = message.from_user

    # TMDb দিয়ে মুভি সার্চ
    search_results = await search_movie(movie_name)

    if not search_results:
        return await message.reply(
            f"❌ No movie found with the name `{movie_name}`.\nPlease check the spelling and try again.",
            quote=True
        )

    # সবচেয়ে কাছাকাছি রেজাল্ট বের করো
    top_result = search_results[0]
    confirmed_movie_name = top_result.get("title")
    poster_path = top_result.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

    # যদি পুরোপুরি মিলে না, সাজেশন দাও
    if confirmed_movie_name.lower() != movie_name.lower():
        suggestions = "\n".join(
            [f"`{movie.get('title')}` ({movie.get('release_date', 'N/A')[:4]})" for movie in search_results[:5]]
        )
        return await message.reply(
            f"❗ Did you mean one of these?\n\n{suggestions}\n\n"
            "Please send the exact movie name again using `/requestbots` command.",
            quote=True
        )

    # ডেটাবেজে রিকোয়েস্ট সেভ করো
    await add_movie_request(user.id, confirmed_movie_name)

    # অ্যাডমিনদের কাছে রিকোয়েস্ট পাঠাও
    await send_movie_request_to_admins(client, confirmed_movie_name, user.id, user.first_name, poster_url)

    await message.reply(
        f"✅ Your request for `{confirmed_movie_name}` has been successfully submitted!\n"
        "We will notify you once it's available.\n\n"
        "__Thanks for using our service! Stay tuned!__",
        quote=True
    )

# অ্যাডমিনদের কাছে রিকোয়েস্ট পাঠানোর ফাংশন
async def send_movie_request_to_admins(client: Client, movie_name: str, user_id: int, user_name: str, poster_url: str = None):
    request_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    caption = f"""
📩 **New Movie Request Received!**

🎬 **Movie:** `{movie_name}`
👤 **Requested By:** [{user_name}](tg://user?id={user_id})
🆔 **User ID:** `{user_id}`
🕰️ **Requested At:** `{request_time}`

📣 _Please Approve or Reject the request from below._
"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}_{movie_name}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}_{movie_name}")
        ]
    ])

    # Send to LOG_CHANNEL + all admins
    target_chats = set([LOG_CHANNEL] + ADMIN_IDS)

    for chat_id in target_chats:
        try:
            if poster_url:
                await client.send_photo(
                    chat_id=chat_id,
                    photo=poster_url,
                    caption=caption,
                    reply_markup=buttons
                )
            else:
                await client.send_message(
                    chat_id=chat_id,
                    text=caption,
                    reply_markup=buttons
                )
        except Exception as e:
            print(f"Failed to send request to {chat_id}: {e}")

# Approve/Reject বাটন হ্যান্ডলার
@Client.on_callback_query(filters.regex(r"^(approve|reject)_(\d+)_(.+)"))
async def approve_or_reject_request(client: Client, callback_query: CallbackQuery):
    action, user_id, movie_name = callback_query.data.split("_", 2)
    user_id = int(user_id)

    if callback_query.from_user.id not in ADMIN_IDS:
        return await callback_query.answer("❌ You are not authorized to perform this action.", show_alert=True)

    movie_details = await get_movie_details(movie_name)
    poster_url = f"https://image.tmdb.org/t/p/w500{movie_details.get('poster_path')}" if movie_details and movie_details.get("poster_path") else None
    overview = movie_details.get("overview", "No description available.") if movie_details else "No description available."

    status_text = (
        "**Congratulations!**\n\n✅ Your requested movie has been **Accepted** and will be uploaded shortly. Stay connected!"
        if action == "approve"
        else "**Oops!**\n\n❌ Unfortunately, your requested movie has been **Rejected**. We apologize for the inconvenience."
    )

    caption = f"""
🎬 **{movie_name}**
📝 **Description:** {overview[:400]}...

{status_text}

__Thanks for understanding!__
"""

    try:
        if poster_url:
            await client.send_photo(user_id, poster_url, caption=caption)
        else:
            await client.send_message(user_id, caption)
    except Exception as e:
        print(f"❗ Failed to notify user {user_id}: {e}")

    # ডেটাবেজ থেকে রিকোয়েস্ট মুছে ফেলো
    await delete_movie_request(user_id, movie_name)

    # মেসেজ আপডেট করো
    new_caption = (
        f"✅ Approved!\n\n🎬 `{movie_name}`\n👤 [User](tg://user?id={user_id})"
        if action == "approve"
        else f"❌ Rejected!\n\n🎬 `{movie_name}`\n👤 [User](tg://user?id={user_id})"
    )

    try:
        await callback_query.message.edit_caption(caption=new_caption)
    except Exception as e:
        print(f"❗ Failed to edit admin message: {e}")

    await callback_query.answer(f"Request {action.title()}ed!", show_alert=True)

# রিকোয়েস্ট লিস্ট দেখানোর কমান্ড
@Client.on_message(filters.command("requestlist") & filters.user(ADMIN_IDS))
async def request_list(client: Client, message: Message):
    data = await get_all_requests()
    if not data:
        return await message.reply("📭 No pending movie requests.")

    text = "🎞️ **Pending Movie Requests:**\n\n"
    for i, req in enumerate(data, start=1):
        requested_at = req.get("requested_at", "N/A")
        text += f"{i}. `{req['movie_name']}` - [User](tg://user?id={req['user_id']}) (🕰️ {requested_at})\n"

    await message.reply(text)

# সব রিকোয়েস্ট ক্লিয়ার করার কমান্ড
@Client.on_message(filters.command("clearrequests") & filters.user(ADMIN_IDS))
async def clear_requests(client: Client, message: Message):
    await clear_all_requests()
    await message.reply("✅ All pending movie requests have been cleared.")

# ইউজার নিজে নিজের রিকোয়েস্ট বাতিল করতে পারবে
@Client.on_message(filters.command("cancelrequest") & filters.private)
async def cancel_request(client: Client, message: Message):
    user = message.from_user
    movie_name = " ".join(message.command[1:]) if len(message.command) > 1 else None

    if not movie_name:
        return await message.reply("❌ Usage: `/cancelrequest Movie Name`", quote=True)

    try:
        await delete_movie_request(user.id, movie_name)
        await message.reply(f"✅ Your request for `{movie_name}` has been cancelled successfully!\n\n__Feel free to request again anytime!__", quote=True)
    except Exception as e:
        await message.reply(f"❌ Failed to cancel request: {e}", quote=True)













from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import requests

# Configurations (Replace these)
TMDB_API_KEY = "c3443ed2f96cd615e3badf6b68c8a689"  # এখানে তোমার TMDB API KEY বসাও
POST_CHANNEL_ID = -1002589776901    # এখানে তোমার চ্যানেল আইডি বসাও

# In-memory user session dict
movie_data = {}

@Client.on_message(filters.command("share_movie") & filters.private)
async def start_share_movie(client, message: Message):
    await message.reply_text("Please send your movie or series name:")
    movie_data[message.from_user.id] = {"step": "ask_name"}

@Client.on_message(filters.text & filters.private)
async def handle_text(client, message: Message):
    user_id = message.from_user.id
    if user_id not in movie_data:
        return

    step = movie_data[user_id].get("step")

    if step == "ask_name":
        query = message.text
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
        response = requests.get(url).json()
        results = response.get("results", [])

        if not results:
            movie_data.pop(user_id, None)
            return await message.reply("No results found.")

        movie_data[user_id].update({
            "step": "select_movie",
            "results": results,
            "page": 0
        })
        await show_result(client, message.chat.id, user_id)

    elif step == "ask_link":
        link = message.text.strip()
        if not link.startswith("http"):
            return await message.reply("Please send a valid URL starting with http or https.")

        selected = movie_data[user_id]["results"][movie_data[user_id]["page"]]
        title = selected.get("title") or selected.get("name")
        poster = selected.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else None

        caption = f"**{title}**\n\nClick the button below to watch/download."
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Get Now", url=link)]])

        if poster_url:
            await client.send_photo(POST_CHANNEL_ID, poster_url, caption=caption, reply_markup=buttons)
        else:
            await client.send_message(POST_CHANNEL_ID, caption, reply_markup=buttons)

        await message.reply("✅ Movie post has been shared to your channel.")
        movie_data.pop(user_id, None)

async def show_result(client, chat_id, user_id):
    data = movie_data[user_id]
    page = data["page"]
    result = data["results"][page]
    title = result.get("title") or result.get("name")
    year = result.get("release_date", "N/A")[:4]
    overview = result.get("overview", "No description available.")
    poster = result.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else None

    caption = f"**{title} ({year})**\n\n{overview}"
    buttons = [
        [
            InlineKeyboardButton("⬅️ Prev", callback_data="prev"),
            InlineKeyboardButton("➡️ Next", callback_data="next")
        ],
        [InlineKeyboardButton("✅ Select", callback_data="select")]
    ]

    if poster_url:
        await client.send_photo(chat_id, poster_url, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await client.send_message(chat_id, caption, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^(prev|next|select)$"))
async def handle_pagination(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = movie_data.get(user_id)
    if not data:
        return await callback_query.answer("Session expired. Please try /share_movie again.", show_alert=True)

    if callback_query.data == "prev":
        if data["page"] > 0:
            data["page"] -= 1
        await callback_query.message.delete()
        await show_result(client, callback_query.message.chat.id, user_id)

    elif callback_query.data == "next":
        if data["page"] < len(data["results"]) - 1:
            data["page"] += 1
        await callback_query.message.delete()
        await show_result(client, callback_query.message.chat.id, user_id)

    elif callback_query.data == "select":
        movie_data[user_id]["step"] = "ask_link"
        await callback_query.message.delete()
        await callback_query.message.reply_text("Please send your shareable link.")





