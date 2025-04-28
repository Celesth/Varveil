import os
import yt_dlp
import requests
import subprocess
import time
from config import URL, TIME

DOWNLOAD_FOLDER = "varveil_downloads"
VARLINKS_FOLDER = "Varlinks"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(VARLINKS_FOLDER, exist_ok=True)

LITTERBOX_URL = "https://litterbox.catbox.moe/resources/internals/api.php"
PREFERRED_RESOLUTIONS = ["2160p", "1440p", "1080p", "720p", "480p", "360p"]

def print_banner():
    print("\n=== Varveil Downloader ===\n")

def get_available_formats(video_url):
    ydl_opts = {'quiet': True}
    formats_list = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])

            video_formats = []

            for fmt in formats:
                res = fmt.get('format_note') or f"{fmt.get('height', '')}p"
                vcodec = fmt.get('vcodec', 'none')
                acodec = fmt.get('acodec', 'none')

                if vcodec != 'none':
                    video_formats.append((fmt['format_id'], res, "H.264" if "avc" in vcodec or "h264" in vcodec else "Other"))

            video_formats.sort(key=lambda x: PREFERRED_RESOLUTIONS.index(x[1]) if x[1] in PREFERRED_RESOLUTIONS else len(PREFERRED_RESOLUTIONS))

            formats_list.extend(video_formats)

    except Exception as e:
        print(f"⚠️ Error: {e}")

    return formats_list

def save_link(title, url, litter_url):
    path = os.path.join(VARLINKS_FOLDER, f"{title}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n{url}\n{litter_url}\n{TIME}")
    print(f"Saved link: {path}")

def upload_to_litterbox(filepath, title, url):
    try:
        with open(filepath, "rb") as f:
            r = requests.post(LITTERBOX_URL, files={"fileToUpload": f}, data={"reqtype": "fileupload", "time": TIME})
        if r.ok:
            litter_url = r.text.strip()
            print(f"Uploaded: {litter_url}")
            save_link(title, url, litter_url)
            os.remove(filepath)
            print("Local file deleted.")
        else:
            print(f"❌ Upload failed: {r.text}")
    except Exception as e:
        print(f"⚠️ Upload error: {e}")

def remux_to_h264(input_file):
    if input_file.lower().endswith(".mp4"):
        try:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=nokey=1:noprint_wrappers=1", input_file],
                capture_output=True, text=True
            )
            codec = probe.stdout.strip()
            if codec == "h264":
                print("Already H.264.")
                return input_file
        except Exception as e:
            print(f"⚠️ FFprobe error: {e}")
            return input_file

    output_file = input_file.rsplit(".", 1)[0] + "_remuxed.mp4"
    print("Remuxing...")
    start = time.time()
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_file, "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", output_file
        ], check=True)
        os.remove(input_file)
        print(f"Remux complete in {round(time.time() - start, 2)}s")
        return output_file
    except Exception as e:
        print(f"⚠️ Remux error: {e}")
        return input_file

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        print(f"\rDownloading: {percent} at {speed}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\nDownload complete.")

def varveil(video_url, fmt_id):
    ydl_opts = {
        'format': f"{fmt_id}+bestaudio/best",
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4',
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file = ydl.prepare_filename(info)
            title = info.get("title", "Unknown")

            file = remux_to_h264(file)
            upload_to_litterbox(file, title, video_url)
    except Exception as e:
        print(f"⚠️ Download error: {e}")

if __name__ == "__main__":
    print_banner()
    url = URL if URL else input("Enter URL: ").strip()

    formats = get_available_formats(url)
    if not formats:
        print("❌ No formats.")
        exit()

    print("\nQualities:")
    for i, (fid, res, label) in enumerate(formats, 1):
        print(f"{i}. {res} ({label})")

    try:
        idx = int(input("\nPick number: ")) - 1
        if 0 <= idx < len(formats):
            fmt, _, _ = formats[idx]
            varveil(url, fmt)
        else:
            print("❌ Invalid selection.")
    except ValueError:
        print("❌ Invalid input.")
