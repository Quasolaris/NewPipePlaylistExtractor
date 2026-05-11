#!/usr/bin/env python3

import csv
import sqlite3
import sys
import os
import time
import re
import zipfile
import tempfile
from sqlite3 import Error
from pytubefix import YouTube
from pydub import AudioSegment

class text:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

database_size_limit = 1024**3 # 1GB size limit for DB extraction

def logo():
    print(text.RED + "NewPipe Playlist Extractor" + text.END)

def create_connection(db_file):
    temp_folder = None
    try:
        if db_file.endswith('.zip'):
            with zipfile.ZipFile(db_file) as newpipezip:
                db_info = newpipezip.getinfo('newpipe.db')
                if db_info.file_size > database_size_limit:
                    print(f"{text.RED}newpipe.db is too large ({db_info.file_size} bytes). Exiting.{text.END}")
                    return None, None
                temp_folder = tempfile.TemporaryDirectory()
                db_file = newpipezip.extract('newpipe.db', path=temp_folder.name)
                print(f"Extracted DB to {text.CYAN}{db_file}{text.END}")
        conn = sqlite3.connect(db_file)
        def dict_factory(cursor, row):
            fields = [column[0] for column in cursor.description]
            return {key: value for key, value in zip(fields, row)}
        conn.row_factory = dict_factory
        return conn, temp_folder
    except KeyError:
        print(text.RED + "No newpipe.db found in ZIP." + text.END)
    except Error as e:
        print(text.RED + str(e) + text.END)
    return None, None

def getPlaylists(db_file):
    print("Extracting Playlists...")
    conn, temp_folder = create_connection(db_file)
    if conn is None:
        return None
    cur = conn.cursor()

    # query local playlists (playlist uid and name)
    cur.execute("SELECT uid, name FROM playlists")
    local_playlists = cur.fetchall()

    # query remote playlists (uid, name, url)
    cur.execute("SELECT uid, name, url FROM remote_playlists")
    remote_playlists = cur.fetchall()

    PlaylistDir = {}

    # add local playlists with video URLs
    for pl in local_playlists:
        uid = pl["uid"]
        name = pl["name"]
        cur.execute("""
            SELECT s.url FROM playlist_stream_join psj
            JOIN streams s ON psj.stream_id = s.uid
            WHERE psj.playlist_id = ?
            ORDER BY psj.join_index
        """, (uid,))
        urls = [row["url"] for row in cur.fetchall()]
        PlaylistDir[name] = urls

    # add remote playlists as single URL list
    for pl in remote_playlists:
        name = pl["name"]
        url = pl["url"]
        PlaylistDir[name] = [url]

    conn.close()
    if temp_folder is not None:
        temp_folder.cleanup()

    return PlaylistDir

def downloadPlaylist(folderName, playlist, codec):
    path = "./Playlists/" + folderName
    if not os.path.exists(path):
        os.mkdir(path)
    for song_url in playlist:
        print(text.BLUE + "Downloading: " + song_url + text.END)
        try:
            YouTubeVideo = YouTube(str(song_url))
            songName = YouTubeVideo.streams[0].title
            destination = path + "/"
            if not os.path.exists(destination + songName + "." + codec):
                audio = YouTubeVideo.streams.filter(only_audio=True)[0]
                audioFile = audio.download(output_path=destination)
                if codec != "mp4":
                    given_audio = AudioSegment.from_file(audioFile, format="mp4")
                    base, ext = os.path.splitext(audioFile)
                    newFile = base + "." + codec
                    given_audio.export(newFile, format=codec)
                    os.remove(audioFile)
                else:
                    pass
                print(text.YELLOW + "Waiting 3 sec. for YouTube DDoS protection circumvent" + text.END)
                time.sleep(3)
            else:
                print(text.CYAN + (destination + songName + "." + codec) + " already downloaded" + text.END)
        except Exception as e:
            print(text.RED + str(e) + text.END)
            print("If error is get_throttling_function_name could not find match for multiple")
            print("Read the README error chapter")

def chooseCodec():
    print("=========================")
    print(text.YELLOW + "Note: Audio gets converted from .mp4 to get raw file choose mp4 option." + text.END)
    print("1\t|\tmp3")
    print("2\t|\twav")
    print("3\t|\tflac")
    print("4\t|\taac")
    print("5\t|\topus")
    print("6\t|\tmp4")
    userInput = str(input("Choose codec(default is mp3): "))
    print("=========================")
    codecs = {"1": "mp3", "2": "wav", "3": "flac", "4": "aac", "5": "opus", "6": "mp4"}
    return codecs.get(userInput, "mp3")

def main(db_file):
    logo()
    Playlists = getPlaylists(db_file)
    if Playlists is None or len(Playlists) == 0:
        print("No playlists could be extracted. Exiting.")
        sys.exit()

    playlistCount = len(Playlists)
    print(text.CYAN + str(playlistCount) + text.END + " Playlists extracted ")
    print("=========================")
    print("1\t|\tDownload all playlists")
    print("2\t|\tDownload single playlist")
    print("3\t|\tSave playlists to .csv file")
    print("4\t|\tSave playlists to .txt file")
    print("5\t|\tSave playlists to .m3u8 files")
    print("6\t|\tSave playlists to .md file")
    print("7\t|\tDump contents of database to JSON (debug)")

    userInput = str(input("Choose action: "))
    print("=========================")

    if userInput == "1":
        userCodec = chooseCodec()
        print("Downloading all playlists...")
        for playlist in Playlists:
            print("Downloading playlist: " + text.CYAN + playlist + text.END)
            downloadPlaylist(playlist, Playlists[playlist], userCodec)
        print(text.GREEN + "Done!" + text.END)

    elif userInput == "2":
        playlistIndex = {}
        print("Available playlists")
        index = 0
        for key in Playlists:
            playlistIndex[index] = key
            print("{0} => {1}".format(index, key))
            index += 1
        userInput = str(input("Type playlist index: "))
        chosenPlaylist = playlistIndex.get(int(userInput))
        if chosenPlaylist and chosenPlaylist in Playlists:
            userCodec = chooseCodec()
            downloadPlaylist(chosenPlaylist, Playlists[chosenPlaylist], userCodec)
            print(text.GREEN + "Done!" + text.END)
        else:
            print(text.YELLOW + "Playlist not in data base" + text.END)

    elif userInput == "3":
        print("Saving playlists into /Playlists/playlists.csv")
        os.makedirs("./Playlists", exist_ok=True)
        with open("./Playlists/playlists.csv", "w", newline='', encoding='utf-8') as f:
            writerCSV = csv.writer(f)
            for playlist, urls in Playlists.items():
                writerCSV.writerow([playlist, str(urls)])
        print(text.GREEN + "Done!" + text.END)

    elif userInput == "4":
        print("Saving playlists into /Playlists/playlists.txt")
        os.makedirs("./Playlists", exist_ok=True)
        with open('./Playlists/playlists.txt', 'w', encoding='utf-8') as writerTXT:
            for playlist in Playlists:
                writerTXT.write("=========================\n")
                writerTXT.write(playlist + "\n")
                writerTXT.write("=========================\n")
                for url in Playlists[playlist]:
                    writerTXT.write(url + "\n")
        print(text.GREEN + "Done!" + text.END)

    elif userInput == "5":
        print("Saving m3u8 playlists into /Playlists/")
        os.makedirs("./Playlists", exist_ok=True)
        for playlist in Playlists:
            playlistpath = './Playlists/' + re.sub('[*"/\\<>:|?]', '_', playlist) + '.m3u8'
            print(f'Writing {playlistpath}')
            with open(playlistpath, 'w', encoding='utf-8') as writerM3U8:
                writerM3U8.write("#EXTM3U\n")
                writerM3U8.write("#PLAYLIST:" + playlist + "\n")
                for song_url in Playlists[playlist]:
                    writerM3U8.write(song_url + "\n")
        print(text.GREEN + "Done!" + text.END)

    elif userInput == "6":
        print("Saving playlists into /Playlists/playlists.md")
        os.makedirs("./Playlists", exist_ok=True)
        with open('./Playlists/playlists.md', 'w', encoding='utf-8') as writerMD:
            for playlist in Playlists:
                writerMD.write(playlist + "\n")
                writerMD.write("=========================\n\n")
                for url in Playlists[playlist]:
                    writerMD.write(f"* [{url}]({url})\n")
                writerMD.write("\n")
        print(text.GREEN + "Done!" + text.END)

    elif userInput == "7":
        import json
        print("Dumping all data managed by NewPipe Playlist Extractor to /Playlists/playlists.json")
        os.makedirs("./Playlists", exist_ok=True)
        with open('./Playlists/playlists.json', 'w', encoding='utf-8') as writerJSON:
            json.dump(Playlists, writerJSON, ensure_ascii=False, indent=4)
        print(text.GREEN + "Done!" + text.END)

    else:
        print(text.YELLOW + "Wrong input, ending script" + text.END)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("""Usage: python3 main.py <newpipe.db or zip>

To use this script:

1. Open the NewPipe app menu > Settings > Backup and Restore.
2. Extract the database as .ZIP file.
3. Run this script with path to zip or newpipe.db file.

Examples:

$ python3 main.py NewPipeBackup.zip
$ python3 main.py newpipe.db
""")
