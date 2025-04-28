import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re

# TMDB API Key
TMDB_API_KEY = 'c3443ed2f96cd615e3badf6b68c8a689'
POST_CHANNEL_ID = -1002589776901  # Put your actual post channel ID here
ADMIN_ID = 7862181538  # Replace with your actual admin ID

# Function to clean movie title (remove unnecessary parts)
def clean_movie_title(title: str) -> str:
    """
    Remove unnecessary parts like video quality, encoding type, language, year, etc.
    """
    title = re.sub(r'\b(?:720p|1080p|AMZN|WEB-DL|HDRip|x264|x265|HEVC|Hindi|Dubbed|BluRay|DVDRip|CAM|5.1|MP4|MKV|WEBM|FLAC|MP3|Dub)\b', '', title)
    title = re.sub(r'\b(?:2023|2022|2021|2020|2019|2018|2017|2016|2015|2014|2013|2012|2011|2010)\b', '', title)  # Remove year
    title = re.sub(r'\s+', ' ', title).strip()  # Remove extra spaces
    return title

# Function to fetch movie details from TMDB
def fetch_movie_details(movie_title: str):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(url)
    data = response.json()

    if data['results']:
        movie = data['results'][0]
        movie_title = movie['title']
        movie_description = movie['overview']
        movie_image = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None
        movie_rating = movie['vote_average']

        return {
            "title": movie_title,
            "description": movie_description,
            "image": movie_image,
            "rating": movie_rating
        }
    return None

# Function to post movie details automatically to the channel
async def post_movie_to_channel(client, movie_title: str):
    movie_details = fetch_movie_details(movie_title)
    if movie_details:
        text = f"""
        **🎬 {movie_details['title']}**

        {movie_details['description']}

        ⭐ **Rating:** {movie_details['rating']}/10

        📽️ **Watch Now**: [Click Here](https://www.example.com/movie-link)  # Replace with actual movie link
        """
        buttons = [
            [
                InlineKeyboardButton("Get Now", url="https://www.example.com/movie-link"),  # Replace with actual movie link
                InlineKeyboardButton("Search Now", url="https://www.example.com/search-now")  # Replace with actual search link
            ]
        ]

        # Send the post message with inline buttons and image
        await client.send_photo(
            POST_CHANNEL_ID,
            photo=movie_details['image'],
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# Function to track new movie uploads in the channel
@Client.on_message(filters.chat(POST_CHANNEL_ID) & filters.media)
async def on_new_movie(client, message):
    if message.photo:
        # Extract movie title (assuming the title is included in the message caption)
        movie_title = message.caption or "Untitled Movie"
        
        # Clean the movie title (remove unnecessary parts)
        cleaned_title = clean_movie_title(movie_title)
        
        # Post movie details using TMDB API
        await post_movie_to_channel(client, cleaned_title)

