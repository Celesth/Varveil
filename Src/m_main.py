import os
import yt_dlp
import subprocess
import time
from config import URL, TIME
from colorama import Fore, Style, init

# === Init Colorama ===
init(autoreset=True)

# === Configuration ===
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_PATH, "varveil_downloads")
VARLINKS_FOLDER = os.path.join(BASE_PATH, "Varlinks")
PREFERRED_RESOLUTIONS = ["2160p", "1440p", "1080p", "720p", "480p", "360p"]

# === Setup ===
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(VARLINKS_FOLDER, exist_ok=True)

# === Helper Functions ===
def print_banner():
    print("\n" + "="*35)
    print(Fore.CYAN + "          Varveil Downloader")
    print("="*35 + "\n" + Style.RESET_ALL)

def print_section(title):
    print(f"\n{Fore.YELLOW}--- {title} ---{Style.RESET_ALL}\n")

def get_available_formats(video_url):
    ydl_opts = {'quiet': True}
    formats_list = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])

            for fmt in formats:
                res = fmt.get('format_note') or f"{fmt.get('height', '')}p"
                ext = fmt.get('ext', '')
                vcodec = fmt.get('vcodec', 'none')

                if vcodec != 'none' and ext in ('mp4', 'webm', 'mkv'):
                    codec_label = (
                        "H.264" if "avc" in vcodec or "h264" in vcodec else
                        "VP9" if "vp9" in vcodec else "Other"
                    )
                    formats_list.append((fmt['format_id'], res, codec_label, ext))

            formats_list.sort(
                key=lambda x: PREFERRED_RESOLUTIONS.index(x[1]) if x[1] in PREFERRED_RESOLUTIONS else len(PREFERRED_RESOLUTIONS)
            )

    except Exception as e:
        print(f"{Fore.RED}⚠️ Error getting formats: {e}{Style.RESET_ALL}")

    return formats_list

def save_link(title, url, local_path):
    path = os.path.join(VARLINKS_FOLDER, f"{title}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n{url}\n{local_path}\n{TIME}")
    print(f"{Fore.GREEN}✓ Saved link: {path}{Style.RESET_ALL}")

def reencode_to_h264(input_file, use_vulkan=False):
    print_section("Re-encoding to H.264")
    output_file = input_file.rsplit(".", 1)[0] + "_reencoded.mp4"
    print(Fore.GREEN + "Re-encoding with " + ("Vulkan GPU" if use_vulkan else "CPU") + "..." + Style.RESET_ALL)
    start = time.time()

    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-c:v", "h264_vulkan" if use_vulkan else "libx264",
        "-preset", "slower", "-crf", "14",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "320k",
        output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"{Fore.GREEN}✓ Re-encoding complete ({round(time.time() - start, 2)}s){Style.RESET_ALL}")
        return output_file
    except Exception as e:
        print(f"{Fore.RED}⚠️ Re-encoding error: {e}{Style.RESET_ALL}")
        return input_file

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        print(f"\r{Fore.CYAN}Downloading: {percent} at {speed}{Style.RESET_ALL}", end='', flush=True)
    elif d['status'] == 'finished':
        print(f"\n{Fore.GREEN}✓ Download complete.{Style.RESET_ALL}")

def varveil(video_url, fmt_id, ext):
    print_section("Starting Download")
    ydl_opts = {
        'format': f"{fmt_id}+bestaudio/best",
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'%(title)s.{ext}'),
        'progress_hooks': [progress_hook],
        'merge_output_format': ext,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
            title = info.get("title", "Unknown")

            reencode = input(Fore.GREEN + "Re-encode to H.264? (y/n): " + Style.RESET_ALL).strip().lower()
            if reencode == 'y' and ext == 'mp4':
                use_vulkan = input(Fore.GREEN + "Use Vulkan GPU acceleration? (y/n): " + Style.RESET_ALL).strip().lower() == 'y'
                final_path = reencode_to_h264(file_path, use_vulkan)
            else:
                final_path = file_path

            save_link(title, video_url, final_path)
    except Exception as e:
        print(f"{Fore.RED}⚠️ Download error: {e}{Style.RESET_ALL}")

# === Main Execution ===
if __name__ == "__main__":
    print_banner()

    url = URL if URL else input("Enter video URL: ").strip()
    formats = get_available_formats(url)

    if not formats:
        print(f"{Fore.RED}❌ No available formats found.{Style.RESET_ALL}")
        exit()

    print_section("Available Qualities")
    for idx, (fmt_id, res, codec, ext) in enumerate(formats, start=1):
        print(f"{idx}. {res} ({codec}, {ext.upper()})")

    try:
        choice = int(input(Fore.GREEN + "\nPick a quality number: " + Style.RESET_ALL)) - 1
        if 0 <= choice < len(formats):
            selected_fmt, _, _, selected_ext = formats[choice]
            varveil(url, selected_fmt, selected_ext)
        else:
            print(f"{Fore.RED}❌ Invalid selection.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}❌ Invalid input.{Style.RESET_ALL}")
