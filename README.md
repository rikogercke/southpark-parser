# About
A southpark downloader which works with the new southpark.de and uses [youtube-dlc](https://github.com/blackjack4494/yt-dlc) and [ffmpeg](https://github.com/FFmpeg/FFmpeg) to download all episodes in 1080p

# Requirements
 - [Python 3](https://www.python.org/downloads/) installed
 - [ffmpeg](https://github.com/FFmpeg/FFmpeg) and [youtube-dlc](https://github.com/blackjack4494/yt-dlc) in the same directory
 - run `pip3 install -r requirements.txt`

## Run
 1. open a shell and run the python script with `python3 run.py` or `python3 run.py -y ` to skip finished downloads

### Progress
The script saves the downloaded files in the `temp` directory and copys the progressed finished files into the `output` folder. While its running, the youtube-dlc and ffmpeg output will be shown.