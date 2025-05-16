# NewPipe Playlist Extractor

![NewPipe Playlist Extractor](/Screenshots/Screenshot_Extractor.png)

### GUI is in development, look at the [GUI chapter](https://github.com/Quasolaris/NewPipePlaylistExtractor#gui) for more information.
<br>

This Python script extracts playlists made with the [NewPipe](https://newpipe.net/) app and allows you to download them as  audio-files. 

When you create a playlist in NewPipe it is not saved as a YouTube playlist and can therefore not be downloaded via a playlist-link. This script allows you to extract the list of videos you have in a playlist and download them as audio files. 

[Buy Me A Coffee!](https://www.buymeacoffee.com/quasolaris)

[Stargazers over time](https://starchart.cc/Quasolaris/NewPipePlaylistExtractor)


### Note: To use script on Windows or Android please see instructions below
### Note: MacOS users, you can follow the Linux guide

# Table of Contents
1. [Features](https://github.com/Quasolaris/NewPipePlaylistExtractor#features)
2. [Codecs](https://github.com/Quasolaris/NewPipePlaylistExtractor#codecs)
3. [Dependencies](https://github.com/Quasolaris/NewPipePlaylistExtractor#dependencies)
4. [Usage](https://github.com/Quasolaris/NewPipePlaylistExtractor#usage)
5. [Linux](https://github.com/Quasolaris/NewPipePlaylistExtractor#linux)
6. [Windows](https://github.com/Quasolaris/NewPipePlaylistExtractor#windows)
7. [Android](https://github.com/Quasolaris/NewPipePlaylistExtractor#android)
8. [GUI](https://github.com/Quasolaris/NewPipePlaylistExtractor#gui)
9. [Errors and Troubleshooting](https://github.com/Quasolaris/NewPipePlaylistExtractor#errors-and-troubleshooting)


## Features
- Download all playlists with chosen audio codec
- Downloads single playlist with chosen audio codec
- Export playlists as CSV file
- playlists.csv to playlists-piped.json
- playlists.csv to freetube-playlists.db
- Export playlists as a TXT file (Format: "Playlist title" \n "URLs")
- Export playlists as a Markdown file
- Export playlists as a M3U8 file 
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
- [pytubefix](https://pypi.org/project/pytubefix/) ``pip3 install pytubefix``
- [db-sqlite3](https://pypi.org/project/db-sqlite3/) ``pip3 install db-sqlite3``
- [pydub](https://pypi.org/project/pydub/) ``pip3 install pydub``
- playlists.csv to freetube-playlists.db
 ``pip3 install yt_dlp``
- [ffmpeg](https://ffmpeg.org/) ``sudo apt install ffmpeg``
- The codec you want to download has to be installed on your machine

## Usage
- Export your NewPipe data ([Click here to see how](https://newpipe.net/FAQ/tutorials/import-export-data/))
- Load it to your PC
- Optionally, extract the newpipe.db file from it
- Run script with path to the NewPipe data ZIP file (`python3 main.py NewPipe_<timestamp>.zip`) or the extracted newpipe.db file (`python3 main.py newpipe.db`)
- python3 playlists-convert-piped.py (playlists.csv to playlists-piped.json)
- python3 playlists-convert-freetube.py
(playlists.csv to freetube-playlists.db)
- Choose action
- Follow instructions
- To update playlists just repeat with new .db or .zip file. Already downloaded files will be ignored
- Enjoy your music!

The playlists get saved into the /Script/Playlists folder

## Linux
Install the dependencies and you are good to go.

## Windows
To use the script on Windows you have to do a few extra steps:

- Download [ffmpeg for Windows](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z)
- Unpack the archive
- Copy all .exe files from /ARCHIVE_NAME/bin
- Paste them inside the /Scripts folder
- Run script

## Android

For a step-by-step installation guide for Android [click here](https://github.com/Quasolaris/NewPipePlaylistExtractor/blob/main/Guides/android_manual.md).

## GUI
![image](https://github.com/user-attachments/assets/70e7c24b-81da-4a61-8968-eef940b1b8a9)

To test the GUI that is in development, checkout the ```gui``` branch and run ```python3 main_gui.py```.

### Features already implemented
- Upload of DB ZIP file, path via CLI is no longer needed
- Selection of multiple songs playlists to donwload, instead of just one
- Simple Select All button if every playlist should be downloaded
- Track count of playlists are shown
- List is searchable 



## [DEPRICATED USE PYTUBEFIX PIP PACKAGE] 
## Errors and Troubleshooting
### get_throttling_function_name: could not find match for multiple

This is an error due to YouTube changing stuff, either to update or simply to attack Pytube, NewPipe and other clients/downloaders.

### First: Check if Pytube has an update, maybe the Pytube team already fixed it.

If no update was published or the error still persists, follow these steps:

1. Go to the pytube package folder (normally: \~/.local/lib/python3.9/site-packages/pytube  or use `pip list -v` to find it if that doesn't work)
2. Open the cipher.py file in an editor of your choice (```nano -c cipher.py``` the -c flag displays the line number where your cursor is)
3. Comment out the following lines: 272 and 273
4. Paste the following regex beneath the lines you just commented out (Make sure the white spaces are correct, it is Python after all):
```python
r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
```
5. Now go to line 290 (or 288 if you deleted the regex lines instead of commenting them out) with CTRL+_ in nano you can jump to a specific line.
6. Comment the following line out: 
```python
nfunc=function_match.group(1)),
```

7. Right underneath the now commented out line, place the following: 
```python
nfunc=re.escape(function_match.group(1))),
```
The file sector you changed should now look like this:
```python
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
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
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


### AttributeError: 'NoneType' object has no attribute 'span'

This is an error due to YouTube changing stuff, either to update or simply to attack Pytube, NewPipe and other clients/downloader. See https://github.com/pytube/pytube/issues/1499#issuecomment-1473022893 for the issue and the fix.

1. First: Check if Pytube has an update, maybe the Pytube team already fixed it. If no update was published or the error still persists, follow these steps:
2. Go to the pytube package folder (normally: \~/.local/lib/python3.9/site-packages/pytube or use `pip list -v` to find it if that doesn't work).
3. Modify {path to pip packages}/pytube/cipher.py:


```
        transform_plan_raw = find_object_from_startpoint(raw_code, match.span()[1] - 1)
```

to 

```
        transform_plan_raw = js
```

4. Save the file.
5. Try again.
