# NewPipe Playlist Extractor

![NewPipe Playlist Extractor](/Screenshots/Screenshot_Extractor.png)

This Python script extracts playlists made inside the [NewPipe]('https://newpipe.net/') app and allows you to download them as .mp3 files.

## Usage
- Export your NewPipe data ([Click here to see how]('https://newpipe.net/FAQ/tutorials/import-export-data/'))
- Load it to your PC
- Extract it (We are interested into your newpipe.db file)
- Run script with path to your newpipe.db file ``$python3 main.py newpipe.db``
- Choose action
- To update playlists just repeat with new .db file, already downloaded files get ignored
- Enjoy your music!

The playlists get saved into the /Script/Playlists folder

## Features
- Downloads all playlists as MP3 and saves them inside folders named after playlist
- Downloads single playlist and saves it as MP3 in folder named after playlist
- Exports playlists as CSV file
- Exports playlist into a TXT file (Format: "Playlist title" \n "URLs")
- Output is coloured (Because colours are fun!)

## Planed features
It depends if you guys like it and want more of it. If yes, you can recommend features that would be nice and I look to implement them.
I also plan to add the following:
- Download as video
- Choose download path
- Extract newpipe.db directly from archive (so no unpacking of user is needed)

### Dependencies
[pytube]('https://pypi.org/project/pytube/')
