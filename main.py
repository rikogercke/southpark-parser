import urllib.request
import json
import subprocess
from pathlib import Path
from os import listdir
from os.path import isfile, join
from shutil import copyfile
from pathvalidate import sanitize_filename
null = None
episodes = []
souhtparkapiurl = 'https://www.southpark.de/api/episodes/1/18'
customurl = True
debug = True
def download (url, number, title):
    #print(episode)
    temppath = "./temp/"+number
    outputpath = "./output/"
    outputfile = sanitize_filename(number +' - ' + title +'.mp4')
    Path(temppath).mkdir(parents=True, exist_ok=True)
    subprocess.run(['youtube-dlc.exe','--restrict-filenames', url], cwd=temppath)
    onlyfiles = [f for f in listdir(temppath) if isfile(join(temppath, f))]
    with open(temppath + '/parts.txt', 'w') as f:
        for part in onlyfiles:
            if part != 'parts.txt':
                if part != outputfile:
                    f.write("file '"+part+"'\n")
    subprocess.run(['ffmpeg.exe', '-y', '-f', 'concat', '-safe', '0', '-i', 'parts.txt', '-c', 'copy', outputfile], cwd=temppath)
    Path(outputpath).mkdir(parents=True, exist_ok=True)
    copyfile(temppath + '/' + outputfile, outputpath + outputfile)

with urllib.request.urlopen(souhtparkapiurl) as url:
    response = json.loads(url.read().decode())
    loadmore = response['loadMore']

    while loadmore != null:
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
            #print(number + ' ' + title + ': ' + description + ' -- ' + url)
            episode_set = {number: [{"title": title}, {'description': description}, {'url': url}]}
            download(url, number,title)
            episodes.append(episode_set)

        if response['loadMore'] == null:
            loadmore = null


with open('episodes.json', 'w', encoding='utf-8') as f:
    json.dump(episodes, f, ensure_ascii=False, indent=4)


