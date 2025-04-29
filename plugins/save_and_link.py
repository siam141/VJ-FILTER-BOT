from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import requests

# Configurations (Replace these)
TMDB_API_KEY = "YOUR_TMDB_API_KEY"
POST_CHANNEL_ID = -1001234567890  # তোমার চ্যানেল আইডি এখানে বসাও

# User session dict
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

    step = movie_data[user_id]["step"]

    if step == "ask_name":
        query = message.text
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
        response = requests.get(url).json()
        results = response.get("results", [])

        if not results:
            return await message.reply("No results found.")

        movie_data[user_id].update({
            "step": "select_movie",
            "results": results,
            "page": 0
        })
        await show_result(client, message.chat.id, user_id)

    elif step == "ask_link":
        link = message.text
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

        await message.reply("Movie post has been shared to the channel.")
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
        return await callback_query.answer("Session expired.", show_alert=True)

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