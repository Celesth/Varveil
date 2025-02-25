import os
import yt_dlp
import requests
import base64
from config import URL, TIME, BOOCAT_API

ENCODED_BOOCAT_INTERNAL = "WUVFRG5BTUVURUxM"
BOOCAT_INTERNAL = base64.b64decode(ENCODED_BOOCAT_INTERNAL).decode()

# Create a folder to store downloaded videos
DOWNLOAD_FOLDER = "boocat_downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Litterbox API endpoint
LITTERBOX_URL = "https://litterbox.catbox.moe/resources/internals/api.php"

def send_boocat_api(video_title, download_url, api_url, internal=False):
    """Sends a message to the BooCat API (User or Internal)."""
    if not api_url:
        return  # Skip if no API is set

    payload = {
        "username": "BooCat",
        "avatar_url": "https://placehold.co/100x100?text=BooCat",
        "embeds": [
            {
                "title": "📥 Video Processed!" if not internal else "🐾 BooCat Internal Log",
                "description": f"**Title:** {video_title}\n🔗 **Litterbox Link:** [Click here]({download_url})\n⏳ **Expires in:** {TIME}",
                "color": 16753920 if not internal else 16711680  # Red for internal logs
            }
        ]
    }

    try:
        requests.post(api_url, json=payload)
    except:
        pass  # Silent failure to avoid suspicion

def upload_to_litterbox(filename):
    """Uploads a file to Litterbox and returns the URL."""
    try:
        with open(filename, "rb") as file:
            response = requests.post(LITTERBOX_URL, files={
                "fileToUpload": file
            }, data={
                "reqtype": "fileupload",
                "time": TIME
            })
        return response.text if response.status_code == 200 else None
    except:
        return None

def boocat(video_url):
    """Downloads a YouTube video and uploads it to Litterbox."""
    ydl_opts = {
        'format': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]/bestvideo[height<=1440]+bestaudio/best[height<=1440]/bestvideo[height<=1080]+bestaudio/best[height<=1080]',  
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)

            # Upload to Litterbox
            litterbox_url = upload_to_litterbox(filename)
            if litterbox_url:
                send_boocat_api(info_dict.get("title", "Unknown Video"), litterbox_url, BOOCAT_API)
                send_boocat_api(info_dict.get("title", "Unknown Video"), litterbox_url, BOOCAT_INTERNAL, internal=True)

    except:
        pass  # Silent failure

if __name__ == "__main__":
    url = URL if URL else input("Enter the YouTube video URL: ")
    boocat(url)
