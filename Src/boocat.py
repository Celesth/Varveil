import os
import yt_dlp
import requests

# Create a folder to store downloaded videos
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Litterbox API endpoint
LITTERBOX_URL = "https://litterbox.catbox.moe/resources/internals/api.php"

def upload_to_litterbox(filename, time="1h"):
    """Uploads a file to Litterbox and returns the URL."""
    try:
        with open(filename, "rb") as file:
            response = requests.post(LITTERBOX_URL, files={
                "fileToUpload": file
            }, data={
                "reqtype": "fileupload",
                "time": time  # Choose from 1h, 12h, 24h, or 72h
            })
        if response.status_code == 200:
            print(f"Uploaded to Litterbox: {response.text}")
        else:
            print(f"Upload failed: {response.text}")
    except Exception as e:
        print(f"An error occurred during upload: {e}")

def download_and_upload(video_url):
    ydl_opts = {
        'format': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]/bestvideo[height<=1440]+bestaudio/best[height<=1440]/bestvideo[height<=1080]+bestaudio/best[height<=1080]',  
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            print(f"Downloaded video saved as: {filename}")

            # Upload to Litterbox
            upload_to_litterbox(filename, time="24h")  # Change time as needed

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    url = input("Enter the YouTube video URL: ")
    download_and_upload(url)
