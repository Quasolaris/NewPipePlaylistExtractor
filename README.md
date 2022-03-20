# NewPipe Playlist Extractor

![NewPipe Playlist Extractor](/Screenshots/Screenshot_Extractor.png)

This Python script extracts playlists made with the [NewPipe](https://newpipe.net/) app and allows you to download them as  audio-files. 

When you create a playlist in NewPipe it is not saved as a YouTube playlist and can therefore not be downloaded via a playlist-link. This script allows you to extract the list of videos you have in a playlist and downlaod them as audio files. 

#### Note: I write and test the script on Linux, I will start testing on Windows soon to ensure it also works on other OSs


## Features
- Download all playlists with chosen audio codec
- Downloads single playlist with chosen audio codec
- Exports playlists as CSV file
- Exports playlist into a TXT file (Format: "Playlist title" \n "URLs")
- Output is coloured (Because colours are fun!)


## Supported Audio Codecs
- mp3
- wav
- flac
- acc
- opus
- mp4


## Usage
- Export your NewPipe data ([Click here to see how](https://newpipe.net/FAQ/tutorials/import-export-data/))
- Load it to your PC
- Extract it (You will need the newpipe.db file)
- Run script with path to your newpipe.db file ``$python3 main.py newpipe.db``
- Choose action
- Follow instructions
- To update playlists just repeat with new .db file, already downloaded files get ignored
- Enjoy your music!

The playlists get saved into the /Script/Playlists folder

## Use on Andriod with Tremux
- Install [Tremux](https://termux.com/)

- Make a folder named /NewPipe inside the Tremux folder

- Download the main.py from the repo and move into the /NewPipe folder

- Create a Playlists folder /NewPipe/Playlists

- Move your newpipe.db into the /NewPipe folder

- Now open a Tremux session and type following:

``$pkg install root-repo``<br>
``$pkg update``<br>
``$pkg install python``<br>
``$pip install db-sqlite3``<br>
``$pip install pydub``<br>
``$pkg install ffmpeg``<br>

- Now Tremux is ready for the script

``$cd ./NewPipe``<br>
``$python main.py newpipe.db``

- Choos your options and download the playlists

- Move your playlists outside to the Music folder

Now you can listen to the downloaded music on your phone.

### Dependencies
- [pytube](https://pypi.org/project/pytube/) ``$pip install pytube``
- [db-sqlite3](https://pypi.org/project/db-sqlite3/) ``$pip install db-sqlite3``
- [pydub](https://pypi.org/project/pydub/) ``$pip install pydub``
- [ffmpeg](https://ffmpeg.org/) ``sudo apt install ffmpeg``
- The codec you want to download has to be  installed on your machine
