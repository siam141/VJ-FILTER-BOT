import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.today_movies_db import get_today_movies, clear_today_movies

POST_CHANNEL_ID = -1002589776901  # Put your actual post channel ID here
ADMIN_ID = 7862181538  # Replace with your actual admin ID

def remove_usernames_from_title(title: str) -> str:
    # Regular expression to match '@username' or '@some_text'
    return re.sub(r'@[\w_]+', '', title).strip()  # Remove '@' followed by word characters or underscores

def replace_underscore_with_space(title: str) -> str:
    # Replace underscores with spaces if no underscore exists
    if "_" not in title:
        return title.replace("_", " ")  # Replace _ with a space
    return title

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    # Fetch today's movies from your database
    movies = await get_today_movies()

    if not movies:
        await message.reply("тЭМ No movies found for today!")
        return

    # Building movie list with clickable titles
    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)  # Remove username if any
        movie_title = replace_underscore_with_space(movie_title)  # Replace _ with space if no _ found

        # Make the movie title clickable by adding a link with movie_title
        movie_list += f"**{idx}.** [ЁЯОм {movie_title}](tg://user?id={message.from_user.id})\n\n"  # This will allow the title to be clickable

    # Send the movie list as a reply
    await message.reply(
        f"**ЁЯУЕ Today's Movie List:**\n\n{movie_list}",
        quote=True
    )

@Client.on_message(filters.command("postlist"))
async def post_today_movies(client, message):
    # Fetch today's movies from your database
    movies = await get_today_movies()

    if not movies:
        await message.reply("тЭМ No movies available to post today!")
        return

    # Build the movie list with buttons
    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)  # Remove username if any
        movie_title = replace_underscore_with_space(movie_title)  # Replace _ with space if no _ found

        # Make the movie title clickable by adding a link with movie_title
        movie_list += f"**{idx}.** [ЁЯОм {movie_title}](tg://user?id={message.from_user.id})\n\n"  # This will allow the title to be clickable

    # Inline buttons setup for action
    buttons = [
        [
            InlineKeyboardButton("Get Now", url="https://www.example.com/movie-link"),  # Replace with actual movie link
            InlineKeyboardButton("Search Now", url="https://www.example.com/search-now")  # Replace with actual search link
        ]
    ]

    # Send the post message with inline buttons
    await client.send_message(
        POST_CHANNEL_ID,
        movie_list,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command("clear_today_list") & filters.user(ADMIN_ID))
async def clear_today_movie_list(client, message):
    # Clear today's movie list in the database
    await clear_today_movies()  # This will now work after implementation

    # Notify the admin
    await message.reply("тЬЕ Today's movie list has been cleared successfully!")















import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import BOT_TOKEN, TMDB_API_KEY  # info.py থেকে BOT_TOKEN এবং TMDB_API_KEY ইনপোর্ট করা

app = Client("movie_bot", bot_token=BOT_TOKEN)

# TMDb API মাধ্যমে মুভি অনুসন্ধান
def search_movie(query, page=1):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=en-US&page={page}&include_adult=false"
    response = requests.get(url).json()
    return response['results'], response['total_pages']

# চ্যানেলে মুভি পোস্ট করার জন্য একটি ফাংশন
def post_movie_to_channel(channel_id, movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url).json()
    movie_title = response['title']
    movie_description = response['overview']
    movie_image = f"https://image.tmdb.org/t/p/w500{response['poster_path']}"

    # চ্যানেলে পোস্ট করতে হবে
    app.send_photo(
        chat_id=channel_id,
        photo=movie_image,
        caption=f"**{movie_title}**\n\n{movie_description}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Watch Now", url=f"https://t.me/{app.username}")]
        ])
    )

# /post_channel কমান্ড
@app.on_message(filters.command("post_channel"))
async def post_channel(client, message):
    # চ্যানেল আইডি যাচাই করা
    if len(message.command) < 2:
        await message.reply("আপনার চ্যানেল আইডি প্রদান করুন /post_channel {channel id}")
        return
    
    channel_id = message.command[1]
    await message.reply("আপনি কোন মুভিটি পোস্ট করতে চান?")
    
    # মুভির নাম গ্রহণ করা
    response = await client.listen(message.chat.id)
    movie_name = response.text
    
    # TMDb API থেকে মুভি সার্চ করা
    movies, total_pages = search_movie(movie_name)
    
    # যদি মুভি পাওয়া যায়
    if movies:
        current_page = 1  # শুরুতে প্রথম পেজ
        keyboard = []
        
        def generate_keyboard(page):
            # সার্চ রেজাল্টের জন্য কীবোর্ড তৈরি করা
            movies, _ = search_movie(movie_name, page)
            keyboard.clear()
            
            for i, movie in enumerate(movies[:5]):  # প্রথম 5টি মুভি দেখাবে
                keyboard.append([InlineKeyboardButton(movie['title'], callback_data=f"movie_{movie['id']}")])
            
            # নেক্সট ও প্রিভিয়াস বাটন সহ
            if page > 1:
                keyboard.append([InlineKeyboardButton("Prev", callback_data=f"prev_{page}")])
            if page < total_pages:
                keyboard.append([InlineKeyboardButton("Next", callback_data=f"next_{page}")])
            
            return InlineKeyboardMarkup(keyboard)

        # প্রথম পেজের কীবোর্ড তৈরি করা
        markup = generate_keyboard(current_page)
        await message.reply(
            "মুভি নির্বাচন করুন:",
            reply_markup=markup
        )
    else:
        await message.reply("কোনো মুভি পাওয়া যায়নি, আবার চেষ্টা করুন।")

@app.on_callback_query()
async def callback_query(client, callback_query):
    data = callback_query.data
    channel_id = callback_query.message.chat.id
    movie_id = None
    current_page = 1
    
    # যদি মুভি সিলেক্ট করা হয়
    if data.startswith("movie_"):
        movie_id = data.split("_")[1]
        # চ্যানেলে মুভি পোস্ট করা
        await post_movie_to_channel(channel_id, movie_id)
        await callback_query.answer("মুভি পোস্ট করা হয়েছে!")

    # প্রিভিয়াস বা নেক্সট বাটনের জন্য কোড
    if data.startswith("prev_"):
        current_page = int(data.split("_")[1]) - 1
        markup = generate_keyboard(current_page)
        await callback_query.message.edit(
            "মুভি নির্বাচন করুন:",
            reply_markup=markup
        )
    
    if data.startswith("next_"):
        current_page = int(data.split("_")[1]) + 1
        markup = generate_keyboard(current_page)
        await callback_query.message.edit(
            "মুভি নির্বাচন করুন:",
            reply_markup=markup
        )

