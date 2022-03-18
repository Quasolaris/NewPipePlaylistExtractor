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



#===== Database extract SQlite by rachmadaniHaryono, found on comment: https://github.com/TeamNewPipe/NewPipe/issues/1788#issuecomment-500805819
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
#=====

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
def downloadPlaylist(folderName, playlist):

    path = "./Playlists/" + folderName

    if(not os.path.exists(path)):
        os.mkdir("./Playlists/" + folderName)

    # download audio
    for videoURL in playlist:
        
        if(checkIfAvaiable):
            
            print("Downloading: " + videoURL)
            try:
                YouTubeVideo = YouTube(str(videoURL))

                songName = YouTubeVideo.streams[0].title
                destination = path + "/"

            
                audio = YouTubeVideo.streams.filter(only_audio=True).first()
                audioFile = audio.download(output_path=destination)

                base, ext = os.path.splitext(audioFile)
                new_file = base + '.mp3'
                os.rename(audioFile, new_file)
            except  Exception as e: 
                print(e)
                


        else:
            print(videoURL + " not avaiable in your location (Try a VPN)")

    

# taken from S P Sharan: https://stackoverflow.com/questions/68818442/how-to-check-if-a-youtube-video-exists-using-python
def checkIfAvaiable(url):
    pattern = '"playabilityStatus":{"status":"ERROR","reason":"Video unavailable"'
    
    request = requests.get(url)
    return False if pattern in request.text else True

def main(db_file):
    
    Playlists = getPlaylists(db_file)

    playlistCount = len(Playlists)

    print(str(playlistCount) + " Playlists extracted: ")

    print("=========================")
    print("1\t|\tDownload all playlists")
    print("2\t|\tDownload single playlist")
    print("3\t|\tSave playlists to .csv file")
    print("4\t|\tSave playlists to .txt file")

    userInput = str(input("Choose action: "))
    print("=========================")
    if(userInput == "1"):

        print("Downlaoding all playlists...")
        for playlist in Playlists:
            print("Downloading playlist: " + playlist)
            downloadPlaylist(playlist, Playlists[playlist])
        print("Done!")

    elif(userInput == "2"):
        print("Avaiable playlists")
        for key in Playlists:
            print("=> " + key)
        
        userInput = str(input("Type playlist name: "))

        if(userInput in Playlists):
            downloadPlaylist(userInput, Playlists[userInput])
        else:
            print("Playlist not in data base")

    elif(userInput == "3"):
        print("Saving playlists into /Playlists/playlists.csv")
        writerCSV = csv.writer(open("./Playlists/playlists.csv", "w"))

        for playlist, songs in Playlists.items():
            writerCSV.writerow([playlist, songs])

    elif(userInput == "4"):
        print("Saving playlists into /Playlists/playlists.txt")

        with open('./Playlists/playlists.txt', 'w') as writerTXT:
            for playlist in Playlists:
                writerTXT.write("=========================\n")
                writerTXT.write(playlist+"")
                writerTXT.write("\n=========================\n")
                for song in Playlists[playlist]:
                    writerTXT.write(song+"\n")

if __name__ == '__main__':
    main(sys.argv[1])


"""
TODO:

choos if:
download single playlist
save URLS into txt file for bulkdonwload with other software
"""