
## BooCat - YouTube Video Downloader
# 
BooCat is a YouTube video downloader that prioritizes 4K resolution and uploads the downloaded videos to Litterbox for temporary storage. It also sends notifications via Discord webhooks.

## Features
#
Downloads YouTube videos in the highest available quality (4K → 2K → 1080p).

Encrypts developer webhook for security.

Automatically uploads videos to Litterbox.

Sends a notification via Discord webhook.

Supports manual and default URL input.


## Installation
#
1. Clone the Repository
```bash
git clone https://github.com/yourusername/boocat.git

cd boocat
```
2. Install Dependencies
```python
pip install -r requirements.txt
```
3. Install FFmpeg (Replit Users)
```shell
apt-get install ffmpeg -y
```

## Configuration
#
1. Create a config.py file and add:


```python
URL = "https://example.com/default-video"
TIME = "1h"  # Litterbox storage duration
BooCatAPI = "YOUR_PUBLIC_WEBHOOK_URL"
```



## Usage
#
Run the script:
```python
python main.py
```

You will be prompted to enter a YouTube video URL. If left blank, it will use the default URL from The [config.py](./Src/config.py)



## Credits

Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading.

Uses [Litterbox](https://litterbox.catbox.moe/tools.php) for temporary file storage.

Uses [FFMPEG](https://www.ffmpeg.org/)


---

