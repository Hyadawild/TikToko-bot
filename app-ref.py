import logging
from dotenv import load_dotenv
import os
import requests
from io import BytesIO

from telethon import TelegramClient, events
from telethon.tl.types import InputFile

from scraper import Scraper  # Assuming the Scraper class is in a file named scraper.py

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO for better visibility
load_dotenv()

api = Scraper()
token = os.getenv("TOKEN")
BOT_USERNAME = "@Your_bot_Bot"

client = TelegramClient("session_name", api_id, api_hash).start(bot_token=token)

@client.on(events.NewMessage(pattern="/start"))
async def start_command(event):
    await event.reply("Support me on: https://trakteer.id/haydarayaya/tip")

@client.on(events.NewMessage(pattern="/help"))
async def help_command(event):
    await event.reply("Available commands: /start, /help, /custom")

@client.on(events.NewMessage(pattern="/custom"))
async def custom_command(event):
    await event.reply("Placeholder for custom functionality")

@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    if event.is_private and "tiktok.com" in event.text:
        try:
            video_data = await hybrid_parsing(event.text)

            if video_data:
                video_stream = video_data["video_stream"]
                music_url = video_data["music_url"]
                caption = video_data["caption"]

                text = f"Link:\n{event.text}\n\nSound:\n{music_url}\n\nCaption:\n{caption}"

                try:
                    await event.reply_video(video=InputFile(video_stream), caption=text)
                except Exception as e:
                    if "Request Entity Too Large" in str(e):
                        await event.reply(
                            "Video is too large, sending link instead." + text
                        )
            else:
                await event.reply("Please send only a TikTok URL.")
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await event.reply("Failed to process the TikTok link. Please try again later.")
    else:
        await event.reply("Please send a TikTok URL in a private message.")

async def hybrid_parsing(url: str) -> dict:
    try:
        result = await api.hybrid_parsing(url)

        video_url = result["video_data"]["nwm_video_url_HQ"]
        music_url = result["music"]["play_url"]["uri"]
        caption = result["desc"]

        response = requests.get(video_url)
        response.raise_for_status()

        video_stream = BytesIO(response.content)

        return {"video_stream": video_stream, "music_url": music_url, "caption": caption}
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return None

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_error()))
async def error_handler(event):
    logging.error(f"Update {event.message.id} caused error {event.message.error}")

if __name__ == "__main__":
    print("Bot started...")
    client.run_until_disconnected()