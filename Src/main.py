import os
import yt_dlp
import requests
from config import URL, TIME

# Create folders for downloads and saved links
DOWNLOAD_FOLDER = "varveil_downloads"
VARLINKS_FOLDER = "Varlinks"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(VARLINKS_FOLDER, exist_ok=True)

# Litterbox API endpoint
LITTERBOX_URL = "https://litterbox.catbox.moe/resources/internals/api.php"

# Preferred resolutions (descending order)
PREFERRED_RESOLUTIONS = ["2160p", "1440p", "1080p", "720p", "480p", "360p"]

def print_banner():
    """Displays the Varveil banner."""
    banner = """
 __      __                  _ _ 
 \ \    / /                 (_) |
  \ \  / /_ _ _ ____   _____ _| |
   \ \/ / _` | '__\ \ / / _ \ | |
    \  / (_| | |   \ V /  __/ | |
     \/ \__,_|_|    \_/ \___|_|_|
                                 
"""
    print(banner)

def get_available_formats(video_url):
    """Fetches available formats and ensures best video + audio if needed."""
    ydl_opts = {'quiet': True}
    available_formats = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])

            video_formats = []
            audio_formats = []

            for fmt in formats:
                res = fmt.get('format_note') or f"{fmt.get('height', '')}p"
                filesize = fmt.get('filesize', "Unknown Size")

                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    video_formats.append((fmt['format_id'], res, filesize, True))  # Combined format
                elif fmt.get('vcodec') != 'none':
                    video_formats.append((fmt['format_id'], res, filesize, False))  # Video-only
                elif fmt.get('acodec') != 'none':
                    audio_formats.append((fmt['format_id'], "Audio", filesize, False))  # Audio-only

            # Sort video formats by preferred resolution order
            video_formats.sort(key=lambda x: PREFERRED_RESOLUTIONS.index(x[1]) if x[1] in PREFERRED_RESOLUTIONS else len(PREFERRED_RESOLUTIONS))

            for fmt_id, res, size, is_combined in video_formats:
                if is_combined:
                    available_formats.append((fmt_id, res, size, True))
                else:
                    best_audio = max(audio_formats, key=lambda x: x[2] if isinstance(x[2], int) else 0, default=None)
                    if best_audio:
                        available_formats.append((f"{fmt_id}+{best_audio[0]}", res, "Merged", False))

    except Exception as e:
        print(f"⚠️ Error fetching formats: {e}")

    return available_formats

def save_link(video_title, youtube_url, litterbox_url):
    """Saves the Litterbox link and YouTube video info to a file."""
    filename = os.path.join(VARLINKS_FOLDER, f"{video_title}.txt")
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"🎥 Video Title: {video_title}\n")
            file.write(f"🔗 YouTube URL: {youtube_url}\n")
            file.write(f"📤 Litterbox Link: {litterbox_url}\n")
            file.write(f"⏳ Expiration Time: {TIME}\n")
        print(f"✅ Saved link in: {filename}")
    except Exception as e:
        print(f"⚠️ Error saving link: {e}")

def upload_to_litterbox(filename, video_title, youtube_url):
    """Uploads a file to Litterbox, deletes the original file, and saves the link."""
    try:
        with open(filename, "rb") as file:
            response = requests.post(LITTERBOX_URL, files={
                "fileToUpload": file
            }, data={
                "reqtype": "fileupload",
                "time": TIME
            })
        if response.status_code == 200:
            litterbox_url = response.text.strip()
            print(f"\n✅ Uploaded to Litterbox: {litterbox_url}")

            save_link(video_title, youtube_url, litterbox_url)

            os.remove(filename)  # Delete file after upload
            print(f"🗑️ Deleted local file: {filename}")

            return litterbox_url
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
    except Exception as e:
        print(f"⚠️ An error occurred during upload: {e}")
        return None

def varveil(video_url, format_id, is_combined):
    """Downloads a YouTube video and uploads it to Litterbox."""
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4' if not is_combined else None,  # Merge if separate
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            video_title = info_dict.get("title", "Unknown Video")

            # Upload to Litterbox and delete the file
            upload_to_litterbox(filename, video_title, video_url)

    except Exception as e:
        print(f"⚠️ An error occurred: {e}")

if __name__ == "__main__":
    print_banner()
    
    url = URL if URL else input("\n🔗 Enter the YouTube video URL: ").strip()

    # Get available formats
    formats = get_available_formats(url)
    if not formats:
        print("❌ No available formats found.")
        exit(1)

    # Display available formats
    print("\n🎥 Available Video Qualities:")
    for i, (fmt_id, fmt_note, fmt_size, is_combined) in enumerate(formats, start=1):
        type_label = "✅ Video + Audio" if is_combined else "🔄 Merged"
        print(f"{i}. {fmt_note} - {fmt_size} ({fmt_id}) [{type_label}]")

    # User selects a format
    try:
        choice = int(input("\n📌 Select a format number to download: ").strip()) - 1
        if 0 <= choice < len(formats):
            selected_format, selected_res, _, is_combined = formats[choice]
            varveil(url, selected_format, is_combined)
        else:
            print("❌ Invalid selection.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
