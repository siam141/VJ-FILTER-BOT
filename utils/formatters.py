# utils/formatters.py

from datetime import datetime

def format_request(movie_name: str, user_name: str, user_id: int, requested_at: datetime):
    requested_time = requested_at.strftime("%d-%m-%Y %I:%M %p")
    return (
        f"📩 **New Movie Request**\n\n"
        f"🎬 **Movie**: `{movie_name}`\n"
        f"👤 **Requested by**: [{user_name}](tg://user?id={user_id})\n"
        f"🆔 **User ID**: `{user_id}`\n"
        f"🕰️ **Requested at**: `{requested_time}`"
    )
