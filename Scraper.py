import requests
import json

from bs4 import BeautifulSoup

async def hybrid_parsing(url: str) -> dict:
    
    response = await requests.get(f"https://your_api_endpoint/{url}")
    
    
    if response.content_type == "application/json":
        data = json.loads(response.content)
        
        video_url = data["video_data"]["nwm_video_url_HQ"]  
        music_url = data["music"]["play_url"]["uri"]
        caption = data["desc"]
    elif response.content_type == "text/html":
        
        soup = BeautifulSoup(response.content, "lxml")
        
        video_url = soup.find("video", {"id": "player"}).get("src")
        music_url = soup.find("audio", {"id": "sound"}).get("src")
        caption = soup.find("meta", {"property": "og:description"}).get("content")

    
    response = requests.get(video_url)
    if response.status_code == 200:
        video_stream = BytesIO(response.content)
    else:
        # Handle error if video download fails.
        raise Exception(f"Failed to download video: {response.status_code}")

    return {"video_stream": video_stream, "music_url": music_url, "caption": caption}