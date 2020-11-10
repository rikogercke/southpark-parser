import urllib.request
import json
import subprocess
from pathlib import Path
from os import listdir
from os.path import isfile, join
from shutil import copyfile, rmtree
from pathvalidate import sanitize_filename
import sys

souhtparkapiurl = 'https://www.southpark.de/api/episodes/1/18'

customurl = True
debug = True
skip = False

episodes = []
null = None

def download (url, number, title):
    temppath = "./temp/"+number
    outputpath = "./output/"
    outputname = sanitize_filename(number +' - ' + title)
    outputfile = outputname +'.mp4'

    Path(outputpath).mkdir(parents=True, exist_ok=True)
    existingfiles = [f for f in listdir(outputpath) if isfile(join(outputpath, f))]

    if skip:
        for file in existingfiles:
            if number in file:
                print('file with name "' + file + '" in ' + outputpath + ' found. skipping: ' + title)
                return

    Path(temppath).mkdir(parents=True, exist_ok=True)

    subprocess.run(['youtube-dlc.exe','--restrict-filenames', url], cwd=temppath)
    onlyfiles = [f for f in listdir(temppath) if isfile(join(temppath, f))]

    with open(temppath + '/parts.txt', 'w') as f:
        for part in onlyfiles:
            if part != 'parts.txt':
                if part != outputfile:
                    f.write("file '"+part+"'\n")

    subprocess.run(['ffmpeg.exe', '-y', '-f', 'concat', '-safe', '0', '-i', 'parts.txt', '-c', 'copy', outputfile], cwd=temppath)
    copyfile(temppath + '/' + outputfile, outputpath + outputfile)
    rmtree(temppath)

if (len(sys.argv) > 1):
    if sys.argv[1] == '-y':
        print('enabled skipping of finished downloads')
        skip = True

with urllib.request.urlopen(souhtparkapiurl) as url:
    response = json.loads(url.read().decode())
    running = True

    while running == True:
        if customurl == True:
            with urllib.request.urlopen(souhtparkapiurl) as url:
                response = json.loads(url.read().decode())
                customurl = False
        else:
            with urllib.request.urlopen('https://www.southpark.de' + response['loadMore']['url']) as url:
                response = json.loads(url.read().decode())
        for episode in response['items']:
            number = episode['meta']['header']['title']
            number = str(number).replace(' • ', '-')
            title = episode['meta']['subHeader']
            description = episode['meta']['description']
            url = episode['url']
            url = 'https://www.southpark.de' + url
            episode_set = {number: [{"title": title}, {'description': description}, {'url': url}]}
            download(url, number,title)
            episodes.append(episode_set)

        if response['loadMore'] == null:
            running = False
            print('finished downloading ' + str(len(episodes)) + ' episodes')


with open('episodes.json', 'w', encoding='utf-8') as f:
    json.dump(episodes, f, ensure_ascii=False, indent=4)


