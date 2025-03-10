
## Varveil - YouTube Video Downloader
# 
Varveil is a YouTube video downloader that prioritizes 4K resolution and uploads the downloaded videos to Litterbox for temporary storage.

## Features
#
Downloads YouTube videos in the highest available quality (4K → 2K → 1080p).

Automatically uploads videos to Litterbox.

Supports manual and default URL input.

## Installation
#
1. Clone the Repository
```bash
git clone https://github.com/Celesth/Varveil.git

```
2. Install Dependencies
```python
pip install -r requirements.txt
```

0. Replit ( For Replit Users )
```sh
In Replit, you can install ffmpeg using Nix by adding it to your replit.nix file.

Steps to Add ffmpeg in Replit:

1. Open your Replit project.


2. Look for a file named replit.nix (if it doesn’t exist, create it).


3. Add or modify the file with this content:

{ pkgs }: {
  deps = [
    pkgs.ffmpeg  # Installs ffmpeg
  ];
}


4. Save the file.


5. Click the "Run" button in Replit or restart the shell by typing:

nix-env -iA nixpkgs.ffmpeg



Verify Installation

Run the following command in the Replit shell to check if ffmpeg is installed:

ffmpeg -version

Now yt-dlp should be able to merge video and audio without issues.
```


## Configuration
#
1. Create a config.py file and add:


```python
URL = "https://example.com/default-video" # if cannot enter the link via the IDE Your runing on
TIME = "1h"  # Litterbox storage duration
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

Uses [FFMPEG](https://www.ffmpeg.org/) For Merging Video And Audio Together


---

