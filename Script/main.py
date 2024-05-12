#!/usr/bin/env python3

import csv
import sqlite3
import sys
import os
import time
import re
from io import StringIO
from sqlite3 import Error
from pytube import YouTube
from pydub import AudioSegment

def logo():
    print(text.RED + "                          _   _                 ______  _                                       ")
    print("                         | \ | |                | ___ \(_)                                      ")
    print("                         |  \| |  ___ __      __| |_/ / _  _ __    ___                          ")
    print("                         | . \` | / _ \\ \ /\ / /|  __/ | || '_ \  / _ \                         ")
    print("                         | |\  ||  __/ \ V  V / | |    | || |_) ||  __/                         ")
    print("                         \_| \_/ \___|  \_/\_/  \_|    |_|| .__/  \___|                         ")
    print("                                                          | |                                   ")
    print("                                                          |_|                                   ")
    print(text.GREEN + "______  _                _  _       _     _____        _                       _                ")
    print("| ___ \| |              | |(_)     | |   |  ___|      | |                     | |               ")
    print("| |_/ /| |  __ _  _   _ | | _  ___ | |_  | |__  __  __| |_  _ __   __ _   ___ | |_   ___   _ __ ")
    print("|  __/ | | / _\` || | | || || |/ __|| __| |  __| \ \/ /| __|| '__| / _\` | / __|| __| / _ \ | '__|")
    print("| |    | || (_| || |_| || || |\__ \| |_  | |___  >  < | |_ | |   | (_| || (__ | |_ | (_) || |   ")
    print("\_|    |_| \__,_| \__, ||_||_||___/ \__| \____/ /_/\_\ \__||_|    \__,_| \___| \__| \___/ |_|   ")
    print("                   __/ |                                                                        ")
    print("                  |___/                                                                         "+ text.END)

def credits():
    print("=============================================")
    print("#           Script by "+ text.PURPLE + "Quasolaris" + text.END + "           #")
    print("#        https://github.com/Quasolaris      #")
    print("#                                           #")
    print("#                                           #")
    print("#           Code snippets used:             #")
    print("# NewPipe SQLite extract: rachmadaniHaryono #")
    print("#         Color class: DelftStack           #")
    print("#                                           #")
    print("#   (For links to the snippets see script)  #")
    print("=============================================")

# https://www.delftstack.com/howto/python/python-bold-text/
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


# Database extract SQlite by rachmadaniHaryono, found on comment: https://github.com/TeamNewPipe/NewPipe/issues/1788#issuecomment-500805819
# --------------------
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        # https://docs.python.org/3/library/sqlite3.html
        def dict_factory(cursor, row):
            fields = [column[0] for column in cursor.description]
            return {key: value for key, value in zip(fields, row)}
        conn.row_factory = dict_factory
        return conn
    except Error as e:
        print(e)
 
    return None


def get_rows(db_file):
    conn = create_connection(db_file)

    sqlCmds = """
    select *
    from streams 
    inner join playlist_stream_join on playlist_stream_join.stream_id = streams.uid
    inner join playlists on playlists.uid == playlist_stream_join.playlist_id
    """
    cur = conn.cursor()
    cur.execute(sqlCmds)
    rows = cur.fetchall()
    return rows
# --------------------

def getPlaylists(db_file):
    """
    Sorting playlists
    Dictionary has playlist name as key 
    and the list of URLs as Value

    Folder gets named after Key, and URLs
    downloaded into given folder
    
    TODO: Add meta data to songs --> Playlist name as Album
    """
    print("Extracting Playlists...")
    rows = get_rows(db_file)

    PlaylistDir = {}
    for row in rows:
        PlaylistDir[row["name"]] = []

    for row in rows:
        PlaylistDir[row["name"]] += [row]
    return PlaylistDir


def downloadPlaylist(folderName, playlist, codec):
    path = "./Playlists/" + folderName
    if(not os.path.exists(path)):
        os.mkdir("./Playlists/" + folderName)

    # download audio
    for song in playlist:
        videoURL = song["url"]
        print(text.BLUE + "Downloading: " + videoURL + text.END)
        try:
            # Download .mp4 of YoutTube URL
            YouTubeVideo = YouTube(str(videoURL))
            songName = YouTubeVideo.streams[0].title
            destination = path + "/"

            # Ignores URL if alreay downloaded in same codec
            if(not os.path.exists(destination + songName + "." + codec)):
                audio = YouTubeVideo.streams.filter(only_audio=True)[0]
                audioFile = audio.download(output_path=destination)

                # if user wants other codec, convert
                if(codec != "mp4"):
                    
                    given_audio = AudioSegment.from_file(audioFile, format="mp4")
                    base, ext = os.path.splitext(audioFile)
                    newFile = base + "."+ codec
                    given_audio.export(newFile, format=codec)
                
                    # removes .mp4 file after conversion is done
                    os.remove(audioFile)
            else:
                print(text.CYAN + (destination + songName + "." + codec) + " already downloaded" + text.END)
                # timeout for 3 sec, to circumwent DDoS protection of Youtube
                print(text.YELLOW + "Waiting 3 sec. for Youtube DDoS protection circumvent" + text.END)
                time.sleep(3)

        except  Exception as e:
            print(text.RED + str(e) + text.END)
            print("If Error is: " + text.RED + "get_throttling_function_name: could not find match for multiple" + text.END)
            print("Read the Error chapter in the README")



def chooseCodec():
    print("=========================")
    print(text.YELLOW + "Note: Audio gets converted from .mp4 to get raw file choose mp4 option.")
    print("When ffmpeg fails it can be that you need to install the chosen codec on your machine."  + text.END)
    print("1\t|\tmp3")
    print("2\t|\twav")
    print("3\t|\tflac")
    print("4\t|\tacc")
    print("5\t|\topus")
    print("6\t|\tmp4")

    userInput = str(input("Choose codec(default is mp3): "))
    print("=========================")

    if(userInput == "1"):
        return "mp3"
    elif(userInput == "2"):
        return "wav"
    elif(userInput == "3"):
        return "flac"
    elif(userInput == "4"):
        return "acc"
    elif(userInput == "5"):
        return "opus"
    elif(userInput == "6"):
        return "mp4"
    else:
        return "mp3"

def main(db_file):
    
    logo()

    Playlists = getPlaylists(db_file)

    playlistCount = len(Playlists)

    print(text.CYAN + str(playlistCount) + text.END + " Playlists extracted ")

    print("=========================")
    print("1\t|\tDownload all playlists")
    print("2\t|\tDownload single playlist")
    print("3\t|\tSave playlists to .csv file")
    print("4\t|\tSave playlists to .txt file")
    print("5\t|\tSave playlists to .m3u8 files")
    print("6\t|\tDump contents of database to JSON (debug)")
    print("7\t|\tCredits")

    userInput = str(input("Choose action: "))
    print("=========================")


    # TODO: clean up mess of print statements, unreadable...
    if(userInput == "1"):
        userCodec = chooseCodec()

        print("Downloading all playlists...")
        for playlist in Playlists:
            print("Downloading playlist: " + text.CYAN + playlist + text.END)
            downloadPlaylist(playlist, Playlists[playlist], userCodec)
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "2"):
        print("Available playlists")
        for key in Playlists:
            print("=> " + key)
        userInput = str(input("Type playlist name: "))

        if(userInput in Playlists):
            userCodec = chooseCodec()
            downloadPlaylist(userInput, Playlists[userInput], userCodec)
            print(text.GREEN + "Done!" + text.END)
            
        else:
            print(text.YELLOW + "Playlist not in data base" + text.END)

    elif(userInput == "3"):
        print("Saving playlists into /Playlists/playlists.csv")
        writerCSV = csv.writer(open("./Playlists/playlists.csv", "w"))

        for playlist, songs in Playlists.items():
            writerCSV.writerow([playlist, [song["url"] for song in songs]])
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "4"):
        print("Saving playlists into /Playlists/playlists.txt")

        with open('./Playlists/playlists.txt', 'w') as writerTXT:
            for playlist in Playlists:
                writerTXT.write("=========================\n")
                writerTXT.write(playlist+"")
                writerTXT.write("\n=========================\n")
                for song in Playlists[playlist]:
                    writerTXT.write(song["url"]+"\n")
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "5"):
        print("Saving m3u8 playlists into /Playlists/")

        for playlist in Playlists:
            playlistpath = './Playlists/' + re.sub('[*"/\\\\<>:|?]', '_', playlist) + '.m3u8'
            print(f'Writing {playlistpath}')
            with open(playlistpath, 'w') as writerM3U8:
                writerM3U8.write("#EXTM3U\n")
                writerM3U8.write("#PLAYLIST:" + playlist + "\n")
                for song in Playlists[playlist]:
                    writerM3U8.write(song["url"]+"\n")
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "6"):
        print("Dumping all data managed by NewPipe Extractor to /Playlists/playlists.json")
        import json
        with open('./Playlists/playlists.json', 'w', encoding='utf-8') as writerJSON:
            json.dump(Playlists, writerJSON, ensure_ascii=False, indent=4)
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "7"):
        credits()

    else:
        print(text.YELLOW + "Wrong input, ending script" + text.END)


if __name__ == '__main__':
    main(sys.argv[1])

