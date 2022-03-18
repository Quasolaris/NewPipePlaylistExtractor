#!/usr/bin/env python3

import csv
import sqlite3
import sys
import os
import requests
import csv
from io import StringIO
from sqlite3 import Error
from pytube import YouTube

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
    print("#    YouTube mp3 Download: GeeksForGeeks    #")
    print("#   YouTube Video Avaiability: S P Sharan   #")
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


#Database extract SQlite by rachmadaniHaryono, found on comment: https://github.com/TeamNewPipe/NewPipe/issues/1788#issuecomment-500805819
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None


def get_rows(db_file):
    conn = create_connection(db_file)

    sqlCmds = """
    select 
            url,
            title,
            playlists.name as playlist_name
    from streams 
    inner join playlist_stream_join on playlist_stream_join.stream_id = streams.uid
    inner join playlists on playlists.uid == playlist_stream_join.playlist_id
    """
    cur = conn.cursor()
    cur.execute(sqlCmds)
    rows = cur.fetchall()
    return rows


def getPlaylists(db_file):
    print("Extracting Playlists...")
    rows = get_rows(db_file)
    
    """
    Sorting playlists
    Dictionary has playlist name as key 
    and the list of URLs as Value

    Folder gets named after Key, and URLs
    downloaded into given folder
    
    TODO: Add meta data to songs --> Playlist name as Album
    """

    PlaylistDir = {"": ""}
    for row in rows:
        PlaylistDir[row[2]] = []

    for row in rows:
        PlaylistDir[row[2]] += [row[0]]
    del PlaylistDir[""]
    return PlaylistDir

# https://www.geeksforgeeks.org/download-video-in-mp3-format-using-pytube/   
def downloadPlaylist(folderName, playlist, fileFormat):

    path = "./Playlists/" + folderName

    if(not os.path.exists(path)):
        os.mkdir("./Playlists/" + folderName)

    # download audio
    for videoURL in playlist:
        
        if(checkIfAvaiable):
            
            print(text.BLUE + "Downloading: " + videoURL + text.END)
            try:
                YouTubeVideo = YouTube(str(videoURL))

                songName = YouTubeVideo.streams[0].title
                destination = path + "/"

            
                audio = YouTubeVideo.streams.filter(only_audio=True)[0]
                audioFile = audio.download(output_path=destination)

                base, ext = os.path.splitext(audioFile)
                new_file = base + "." + fileFormat
                os.rename(audioFile, new_file)
                
            except  Exception as e: 
                print(text.RED + str(e) + text.END)
                


        else:
            print(videoURL + " not avaiable in your location (Try a VPN)")

    

# taken from S P Sharan: https://stackoverflow.com/questions/68818442/how-to-check-if-a-youtube-video-exists-using-python
def checkIfAvaiable(url):
    pattern = '"playabilityStatus":{"status":"ERROR","reason":"Video unavailable"'
    
    request = requests.get(url)
    return False if pattern in request.text else True

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
    print("5\t|\tCredits")

    userInput = str(input("Choose action: "))
    print("=========================")
    if(userInput == "1"):

        userFormat = str(input("Choose format: "))

        print("Downlaoding all playlists...")
        for playlist in Playlists:
            print("Downloading playlist: " + text.CYAN + playlist + text.END)
            downloadPlaylist(playlist, Playlists[playlist], userFormat)
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "2"):
        print("Avaiable playlists")
        for key in Playlists:
            print("=> " + key)
        
        userInput = str(input("Type playlist name: "))

        if(userInput in Playlists):
            userFormat = str(input("Choose format: "))
            downloadPlaylist(userInput, Playlists[userInput], userFormat)
            print(text.GREEN + "Done!" + text.END)
            
        else:
            print(text.YELLOW + "Playlist not in data base" + text.END)

    elif(userInput == "3"):
        print("Saving playlists into /Playlists/playlists.csv")
        writerCSV = csv.writer(open("./Playlists/playlists.csv", "w"))

        for playlist, songs in Playlists.items():
            writerCSV.writerow([playlist, songs])
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "4"):
        print("Saving playlists into /Playlists/playlists.txt")

        with open('./Playlists/playlists.txt', 'w') as writerTXT:
            for playlist in Playlists:
                writerTXT.write("=========================\n")
                writerTXT.write(playlist+"")
                writerTXT.write("\n=========================\n")
                for song in Playlists[playlist]:
                    writerTXT.write(song+"\n")
        print(text.GREEN + "Done!" + text.END)


    elif(userInput == "5"):
        credits()

    else:
        print(text.YELLOW + "Wrong input, ending script" + text.END)


if __name__ == '__main__':
    main(sys.argv[1])

