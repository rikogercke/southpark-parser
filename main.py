import urllib.request
import json
import subprocess
from pathlib import Path
from os import listdir
from os.path import isfile, join
from shutil import copyfile, rmtree
from pathvalidate import sanitize_filename
import sys

# Url to Southpark Api to get all source urls
Southpark_Api_Url = 'https://www.southpark.de/api/episodes/1/18'

Custom_Url = True
Debug = True
Skip_Existing_Episodes = False
running = True

Episodes = []
null = None


def download(Episode_Source_Url, Episode_Identifier, Episode_Title):
    # Paths
    Temp_Path = "./Temp/" + Episode_Identifier
    Output_Path = "./Output/"
    Output_Name = sanitize_filename(Episode_Identifier + ' - ' + Episode_Title)
    Output_File = Output_Name + '.mp4'

    # creating folders
    Path(Output_Path).mkdir(parents=True, exist_ok=True)
    Path(Temp_Path).mkdir(parents=True, exist_ok=True)

    # check if downloaded episodes exist and skip them
    Existing_Files = [f for f in listdir(Output_Path) if isfile(join(Output_Path, f))]
    if Skip_Existing_Episodes:
        for File in Existing_Files:
            if Episode_Identifier in File:
                print('file with name "' + File + '" in ' + Output_Path + ' found. skipping: ' + Episode_Title)
                return

    subprocess.run(['youtube-dlc.exe', '--restrict-filenames','--newline', Episode_Source_Url], cwd=Temp_Path)
    Downloaded_Parts = [f for f in listdir(Temp_Path) if isfile(join(Temp_Path, f))]

    with open(Temp_Path + '/parts.txt', 'w') as f:
        for Episode_Part in Downloaded_Parts:
            if Episode_Part != 'parts.txt':
                if Episode_Part != Output_File:
                    f.write("file '" + Episode_Part + "'\n")

    # running ffmpeg to create a single file out of the 5 parts
    subprocess.run(['ffmpeg.exe', '-y', '-f', 'concat', '-safe', '0', '-i', 'parts.txt', '-c', 'copy', Output_File],
                   cwd=Temp_Path)
    # copy finished episode into the output directory
    copyfile(Temp_Path + '/' + Output_File, Output_Path + Output_File)
    # cleanup
    rmtree(Temp_Path)


# check for arguments
if len(sys.argv) > 1:
    if sys.argv[1] == '-y':
        print('enabled skipping of finished downloads')
        Skip_Existing_Episodes = True

while running:
    if Custom_Url:
        # getting the first api response manually
        with urllib.request.urlopen(Southpark_Api_Url) as Episode_Source_Url:
            Api_Response = json.loads(Episode_Source_Url.read().decode())
            Custom_Url = False
    else:
        with urllib.request.urlopen('https://www.southpark.de' + Api_Response['loadMore']['url']) as Episode_Source_Url:
            Api_Response = json.loads(Episode_Source_Url.read().decode())
    for Episode in Api_Response['items']:
        # getting the necessary data out of the Response
        Episode_Identifier = Episode['meta']['header']['title']
        Episode_Identifier = str(Episode_Identifier).replace(' • ', '-')
        Episode_Title = Episode['meta']['subHeader']
        Episode_Description = Episode['meta']['description']
        Episode_Source_Url = Episode['url']
        Episode_Source_Url = 'https://www.southpark.de' + Episode_Source_Url

        download(Episode_Source_Url, Episode_Identifier, Episode_Title)

        Episode_Infos = {Episode_Identifier: [{"title": Episode_Title}, {'description': Episode_Description},
                                              {'url': Episode_Source_Url}]}
        Episodes.append(Episode_Infos)

    # if no more episodes are available, the process is finished
    if Api_Response['loadMore'] == null:
        running = False
        print('finished downloading ' + str(len(Episodes)) + ' episodes')

# backup all the infos about the Series locally
with open('episodes.json', 'w', encoding='utf-8') as f:
    json.dump(Episodes, f, ensure_ascii=False, indent=4)
