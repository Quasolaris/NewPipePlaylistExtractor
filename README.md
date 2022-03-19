# NewPipe Playlist Extractor

![NewPipe Playlist Extractor](/Screenshots/Screenshot_Extractor.png)

This Python script extracts playlists made with the [NewPipe](https://newpipe.net/) app and allows you to download them as  audio-files. 

When you create a playlist in NewPipe it is not saved as a YouTube playlist and can therefore not be downloaded via a playlist-link. This script allow you to extract the list of videos you have in a playlist and extract them. 

#### Note: I write and test the script on Linux, I will start testing on Windows soon to ensure it also works on other OSs

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

## Planed features
- Extract .db file from .zip
- Download single YouTube link (Playlist or clip)
- Video Download
- Handle wrong user input
- Implement flags
- Full Windows support (at the moment only tested on Linux)

### Dependencies
- [pytube](https://pypi.org/project/pytube/)
- [db-sqlite3](https://pypi.org/project/db-sqlite3/)
- [ffmpeg](https://ffmpeg.org/) ``sudo apt install ffmpeg``
- The codec you want to download has to be  installed on your machine
