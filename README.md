# NewPipe Playlist Extractor

![NewPipe Playlist Extractor](/Screenshots/Screenshot_Extractor.png)

This Python script extracts playlists made with the [NewPipe](https://newpipe.net/) app and allows you to download them as  audio-files. 

When you create a playlist in NewPipe it is not saved as a YouTube playlist and can therefore not be downloaded via a playlist-link. This script allows you to extract the list of videos you have in a playlist and downlaod them as audio files. 

### Note: To use script on Windows or Andriod please see instructions below
### Note: MacOS users, you can follow the Linux guide

[Support me on Pateron](https://www.patreon.com/quasolaris)

# Table of Contents
1. [Features](https://github.com/Quasolaris/NewPipePlaylistExtractor#features)
2. [Codecs](https://github.com/Quasolaris/NewPipePlaylistExtractor#codecs)
3. [Dependencies](https://github.com/Quasolaris/NewPipePlaylistExtractor#dependencies)
4. [Usage](https://github.com/Quasolaris/NewPipePlaylistExtractor#usage)
5. [Linux](https://github.com/Quasolaris/NewPipePlaylistExtractor#linux)
6. [Windows](https://github.com/Quasolaris/NewPipePlaylistExtractor#windows)
7. [Android](https://github.com/Quasolaris/NewPipePlaylistExtractor#android)
8. [Errors and Troubleshooting](https://github.com/Quasolaris/NewPipePlaylistExtractor#errors-and-troubleshooting)


## Features
- Download all playlists with chosen audio codec
- Downloads single playlist with chosen audio codec
- Exports playlists as CSV file
- Exports playlist into a TXT file (Format: "Playlist title" \n "URLs")
- Output is coloured (Because colours are fun!)


## Codecs
The script supports the following codecs:
- mp3
- wav
- flac
- acc
- opus
- mp4

## Dependencies
- [pytube](https://pypi.org/project/pytube/) ``pip install pytube``
- [db-sqlite3](https://pypi.org/project/db-sqlite3/) ``pip install db-sqlite3``
- [pydub](https://pypi.org/project/pydub/) ``pip install pydub``
- [ffmpeg](https://ffmpeg.org/) ``sudo apt install ffmpeg``
- The codec you want to download has to be  installed on your machine

## Usage
- Export your NewPipe data ([Click here to see how](https://newpipe.net/FAQ/tutorials/import-export-data/))
- Load it to your PC
- Extract it (You will need the newpipe.db file)
- Run script with path to your newpipe.db file ``python3 main.py newpipe.db``
- Choose action
- Follow instructions
- To update playlists just repeat with new .db file, already downloaded files get ignored
- Enjoy your music!

The playlists get saved into the /Script/Playlists folder

## Linux
Install the dependencies and you are good to go.

## Windows
To use the script on Windows you have to do a few extra stepps:

- Dowanload [ffmpeg for windows](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z)
- Unpack the archive
- Copy all .exe files from /ARCHIVE_NAME/bin
- Paste them inside the /Scripts folder
- Run script

## Android
To use the script on Android you need to usw Termux and install a few packages:

- Install [Termux](https://termux.com/)

- Make a folder named /NewPipe inside the Termux folder

- Download the main.py from the repo and move into the /NewPipe folder

- Create a Playlists folder /NewPipe/Playlists

- Move your newpipe.db into the /NewPipe folder

- Now open a Termux session and type following:

``pkg install root-repo``<br>
``pkg update``<br>
``pkg install python``<br>
``pip install db-sqlite3``<br>
``pip install pytube``<br>
``pip install pydub``<br>
``pkg install ffmpeg``<br>

- Now Termux is ready for the script

``cd ./NewPipe``<br>
``python main.py newpipe.db``

- Choos your options and download the playlists

- Move your playlists outside to the Music folder

Now you can listen to the downloaded music on your phone.

## Errors and Troubleshooting
### get_throttling_function_name: could not find match for multiple

This is an error due to YouTube changing stuff, either to update or simply to attack Pytube, NewPipe and other clients/downloader. It is resolved with those simple steps:<br>

1. Go to the pytube package folder (normaly: \~/.local/lib/python3.9/site-packages/pytube)
2. Open the cipher.py file in an editor of your choice (```nano -c cipher.py``` the -c flag displays the line number where your cursor is)
3. Comment out the following lines: 272 and 273
4. Paste the following regex beneath the lines you just commented out (Make sure the white spaces are correct, it is python after all):
```
 r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
 r'\([a-z]\s*=\s*([a-zA-Z0-9$]{2,3})(\[\d+\])?\([a-z]\)'
```
5. Now go to line 290 (or 288 if you deleted the regex lines instead of commenting them out) with CTRL+_ in nano you can jump to a specific line.
6. Comment the following line out: 
```
nfunc=function_match.group(1)),
```

7. Right underneath the now commented out line, place the following: 
```
nfunc=re.escape(function_match.group(1))),
```
The file sector you changed should now look like this:
```
function_patterns = [
        # https://github.com/ytdl-org/youtube-dl/issues/29326#issuecomment-865985377
        # https://github.com/yt-dlp/yt-dlp/commit/48416bc4a8f1d5ff07d5977659cb8ece7640dcd8
        # var Bpa = [iha];
        # ...
        # a.C && (b = a.get("n")) && (b = Bpa[0](b), a.set("n", b),
        # Bpa.length || iha("")) }};
        # In the above case, `iha` is the relevant function name
        #r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        #r'\([a-z]\s*=\s*([a-zA-Z0-9$]{3})(\[\d+\])?\([a-z]\)',
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]{2,3})(\[\d+\])?\([a-z]\)'
    ]
    logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        #nfunc=function_match.group(1)),
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise RegexMatchError(
        caller="get_throttling_function_name", pattern="multiple"

```
8. Save and close the file
9. You should now be able to download your playlists again
