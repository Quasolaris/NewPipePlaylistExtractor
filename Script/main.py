#!/usr/bin/env python3


import csv
import sqlite3
import sys
import os
import time
import re
import zipfile
import tempfile
from io import StringIO
from sqlite3 import Error
from pytubefix import YouTube
from pydub import AudioSegment

def logo():
    import shutil
    terminal = shutil.get_terminal_size((0, 0))
    if (terminal.columns < 80):
        print(text.RED + r"""
    _   _               ______ _               
   | \ | |              | ___ (_)              
   |  \| | _____      __| |_/ /_ _ __   ___    
   | . \`|/ _ \ \ /\ / /|  __/| | '_ \ / _ \   
   | |\  |  __/\ V  V / | |   | | |_) |  __/   
   \_| \_/\___| \_/\_/  \_|   |_| .__/ \___|   """ + text.GREEN + r"""
      ______ _             _ _  """ + text.RED + "| |" + text.GREEN + r""" _          """ + text.GREEN + r"""
      | ___ \ |           | (_) """ + text.RED + "|_|" + text.GREEN + r"""| |        
      | |_/ / | __ _ _   _| |_  ___| |_       
      |  __/| |/ _\`| | | | | |/ __| __|      
      | |   | | (_| | |_| | | |\__ \ |_       
      \_|   |_|\__,_|\__, |_|_||___/\__|      
  ____      _         __/ |     _              
|  ___|    | |       |___/     | |             
| |____  __| |_ _ __  __ _  ___| |_  ___  _ __ 
|  __\ \/ /| __| '__|/ _\`|/ __| __|/ _ \| '__|
| |__ >  < | |_| |  | (_| | (__| |_| (_) | |   
\____/_/\_\ \__|_|   \__,_|\___ \__|\___/|_|   
                                               """+ text.END)
    elif (terminal.columns < 96):
        print(text.RED + r"""
                     _   _               ______ _                                
                    | \ | |              | ___ (_)                               
                    |  \| | _____      __| |_/ /_ _ __   ___                     
                    | . \`|/ _ \ \ /\ / /|  __/| | '_ \ / _ \                    
                    | |\  |  __/\ V  V / | |   | | |_) |  __/                    
                    \_| \_/\___| \_/\_/  \_|   |_| .__/ \___|                    
                                                 | |                             
                                                 |_|                             """ + text.GREEN + r"""
______ _             _ _      _   _____      _                   _              
| ___ \ |           | (_)    | | |  ___|    | |                 | |             
| |_/ / | __ _ _   _| |_  ___| |_| |____  __| |_ _ __  __ _  ___| |_  ___  _ __ 
|  __/| |/ _\`| | | | | |/ __| __|  __\ \/ /| __| '__|/ _\`|/ __| __|/ _ \| '__|
| |   | | (_| | |_| | | |\__ \ |_| |__ >  < | |_| |  | (_| | (__| |_| (_) | |   
\_|   |_|\__,_|\__, |_|_||___/\__\____/_/\_\ \__|_|   \__,_|\___ \__|\___/|_|   
                __/ |                                                           
               |___/                                                            """+ text.END)
    else:
        print(text.RED + r"""
                          _   _                 ______  _                                       
                         | \ | |                | ___ \(_)                                      
                         |  \| |  ___ __      __| |_/ / _  _ __    ___                          
                         | . \`| / _ \\ \ /\ / /|  __/ | || '_ \  / _ \                         
                         | |\  ||  __/ \ V  V / | |    | || |_) ||  __/                         
                         \_| \_/ \___|  \_/\_/  \_|    |_|| .__/  \___|                         
                                                          | |                                   
                                                          |_|                                   """ + text.GREEN + r"""
______  _                _  _       _     _____        _                       _                
| ___ \| |              | |(_)     | |   |  ___|      | |                     | |               
| |_/ /| |  __ _  _   _ | | _  ___ | |_  | |__  __  __| |_  _ __   __ _   ___ | |_   ___   _ __ 
|  __/ | | / _\`|| | | || || |/ __|| __| |  __| \ \/ /| __|| '__| / _\`| / __|| __| / _ \ | '__|
| |    | || (_| || |_| || || |\__ \| |_  | |___  >  < | |_ | |   | (_| || (__ | |_ | (_) || |   
\_|    |_| \__,_| \__, ||_||_||___/ \__| \____/ /_/\_\ \__||_|    \__,_| \___| \__| \___/ |_|   
                   __/ |                                                                        
                  |___/                                                                         """+ text.END)

def credits():
    print("""=============================================
#           Script by """+ text.PURPLE + "Quasolaris" + text.END + """            #
#        https://github.com/Quasolaris      #
#                                           #
#                                           #
#           Code snippets used:             #
# NewPipe SQLite extract: rachmadaniHaryono #
#         Color class: DelftStack           #
#                                           #
#   (For links to the snippets see script)  #
=============================================""")

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

database_size_limit = 1024**3 # in bytes. This script will refuse to extract files going over this size.

# Database extract SQlite by rachmadaniHaryono, found on comment: https://github.com/TeamNewPipe/NewPipe/issues/1788#issuecomment-500805819
# --------------------
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return:
        Connection object or None
        Temporary folder, if any
    """
    try:
        """ check if db_file is a zip file.
            If it is, try to connect to newpipe.db inside.
            If not, assume it is the database, uncompressed
        """
        temp_folder = None
        if(db_file[-4:] == '.zip'):
            with zipfile.ZipFile(db_file) as newpipezip:
                db_file = newpipezip.getinfo('newpipe.db')
                # If newpipe.db is not contained, a KeyError exception will be raised.
                # If it is contained, test if uncompressed size is under database_size_limit
                if db_file.file_size > database_size_limit:
                    print(f"{text.RED}newpipe.db weighs {db_file.file_size} bytes. This script will not extract files over {database_size_limit} bytes.{text.END}")
                    return None, None
                temp_folder = tempfile.TemporaryDirectory()
                db_file = newpipezip.extract('newpipe.db', path=temp_folder.name)
                print(f"Automatically extracted database to {text.CYAN}{db_file}{text.END}")
        conn = sqlite3.connect(db_file)
        # https://docs.python.org/3/library/sqlite3.html
        def dict_factory(cursor, row):
            fields = [column[0] for column in cursor.description]
            return {key: value for key, value in zip(fields, row)}
        conn.row_factory = dict_factory
        return conn, temp_folder
    except KeyError:
        print(text.RED + "No newpipe.db item was found. This is not a NewPipe database." + text.END)
    except Error as e:
        print(text.RED + e + text.END)

    return None, None

def get_rows(db_file):
    conn, temp_folder = create_connection(db_file)
    if conn is None: return None

    sqlCmds = """
    select service_id, url, title, stream_type, duration, uploader, uploader_url,
    streams.thumbnail_url as video_thumbnail_url,
    view_count, textual_upload_date, upload_date, is_upload_date_approximation,
    join_index,
    name,
    display_index
    from streams 
    inner join playlist_stream_join on playlist_stream_join.stream_id = streams.uid
    inner join playlists on playlists.uid == playlist_stream_join.playlist_id
    """
    cur = conn.cursor()
    cur.execute(sqlCmds)
    rows = cur.fetchall()
    conn.close()
    if temp_folder is not None:
        temp_folder.cleanup()
        print(f"Data loaded into memory, deleted temporary folder {text.CYAN}{temp_folder.name}{text.END}")
    return rows
# --------------------

def getPlaylists(db_file):
    """
    Sorting playlists
    Dictionary has playlist name as key 
    and a list of videos as value.
    Each video is represented by a dict (see get_rows()).

    Folder gets named after Key, and URLs
    downloaded into given folder
    
    TODO: Add meta data to songs --> Playlist name as Album
    """
    print("Extracting Playlists...")
    rows = get_rows(db_file)
    if rows is None: return None

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
            # Download .mp4 of YouTube URL
            YouTubeVideo = YouTube(str(videoURL))
            songName = YouTubeVideo.streams[0].title
            destination = path + "/"

            # Ignores URL if already downloaded in same codec
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
                # timeout for 3 sec, to circumvent DDoS protection of YouTube
                print(text.YELLOW + "Waiting 3 sec. for YouTube DDoS protection circumvent" + text.END)
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
    if Playlists is None:
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
    print("8\t|\tCredits")

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
                    writerM3U8.write("#EXTINF:" + str(song["duration"]) + "," + song["title"]+"\n")
                    writerM3U8.write(song["url"] + "\n")
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "6"):
        print("Saving playlists into /Playlists/playlists.md")

        with open('./Playlists/playlists.md', 'w') as writerMD:
            for playlist in Playlists:
                writerMD.write(playlist+"")
                writerMD.write("\n=========================\n")
                writerMD.write("\n")
                for song in Playlists[playlist]:
                    if(song["stream_type"] == "LIVE_STREAM"):
                        duration = " (LIVE)"
                    elif(song["duration"] >= 86400):
                        mins, secs = divmod(song["duration"], 60)
                        hours, mins = divmod(mins, 60)
                        days, hours = divmod(hours, 24)
                        duration = " ({:d}:{:02d}:{:02d}:{:02d})".format(days, hours, mins, secs)
                    elif(song["duration"] >= 3600):
                        mins, secs = divmod(song["duration"], 60)
                        hours, mins = divmod(mins, 60)
                        duration = " ({:d}:{:02d}:{:02d})".format(hours, mins, secs)
                    elif(song["duration"] >= 0):
                        mins, secs = divmod(song["duration"], 60)
                        duration = " ({:d}:{:02d})".format(mins, secs)
                    else:
                        duration = ""
                    writerMD.write("* [{:s}]({:s}){:s}\n".format(song["title"], song["url"], duration))
                writerMD.write("\n")
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "7"):
        print("Dumping all data managed by NewPipe Playlist Extractor to /Playlists/playlists.json")
        import json
        with open('./Playlists/playlists.json', 'w', encoding='utf-8') as writerJSON:
            json.dump(Playlists, writerJSON, ensure_ascii=False, indent=4)
        print(text.GREEN + "Done!" + text.END)

    elif(userInput == "8"):
        credits()

    else:
        print(text.YELLOW + "Wrong input, ending script" + text.END)


if __name__ == '__main__':
    if(len(sys.argv) == 2):
        main(sys.argv[1])
    else:
        print("""Usage: python3 main.py <database>

To use this script:
    1. Open the NewPipe menu, open the Settings, and select Backup and Restore.
    2. Tap the option to "Extract the database" as .ZIP file.
    3. Run this script, replacing <database> with the path of the ZIP file.
       (Or else, replace <database> with the path of the file newpipe.db inside.)

Examples:
       $ python3 main.py NEWPIPE.zip
       $ python3 main.py newpipe.db""")


