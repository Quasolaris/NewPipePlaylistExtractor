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
from nicegui import events, ui

class Playlists:
    """
    Class to have the playlists in a static memory position, to have it callable inside async functions
    Use getter and setter for access and update of playlists
    """
    def __init__(self, playlists):
        """
        Takes a dictionary and stores it
        """
        self._playlists = playlists
    @property
    def value(self):
        """Getter method to retrieve the playlists"""
        return self._playlists

    @value.setter
    def value(self, playlists):
        """Setter method to set the playlists"""
        self._playlists = playlists



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

    :param db_file: database file
    :return PlaylistDir: Dictionary with playlists, key is name, value is list of tracks (URL)
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



def main():

    playlists = {}
    playlistsObject = Playlists({})
    playlists = playlistsObject._playlists



    @ui.page('/')
    def page():

    
        async def handle_upload(e: events.UploadEventArguments):

            playlistsObject._playlists = getPlaylists(e.name)
            playlists = playlistsObject._playlists


            if playlists is None:
                print("No playlists could be extracted. Exiting.")
                sys.exit()

            playlistCount = len(playlists)

            ui.html("{0} Playlists Extracted".format(playlistCount))

            print(text.CYAN + str(playlistCount) + text.END + " Playlists extracted ")

            gridPlaylist.options['rowData'] = [{'playlist' : playlist, 'count' : len(playlists[playlist])} for playlist in list(playlists.keys())]
            gridPlaylist.update()

            playlistsGlobal = playlists

     
    
        async def download_selected_rows():
            
            ui.html("Download started")

            playlists = playlistsObject._playlists

            rows = await gridPlaylist.get_selected_rows()
            if rows:
                for row in rows:
                    playlist = row["playlist"]
                    await downloadPlaylist(playlist, playlists[playlist], codecChoice.value)
            else:
                ui.notify('No rows selected', type='negative')
       



        async def handle_theme_change(e: events.ValueChangeEventArguments):
            gridPlaylist.classes(add='ag-theme-balham-dark' if e.value else 'ag-theme-balham',
                         remove='ag-theme-balham ag-theme-balham-dark')



        async def downloadPlaylist(folderName, playlist, setCodec):

            if(setCodec == 1):
                codec = "mp3"
            elif(setCodec == 2):
                codec = "wav"
            elif(setCodec == 3):
                codec = "flac"
            elif(setCodec == 4):
                codec = "acc"
            elif(setCodec == 5):
                codec = "opus"
            elif(setCodec == 6):
                codec = "mp4"
            else:
                codec = "mp3"    

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
            ui.html("Downloading finished - Saved to: {0} - Used Codec: {1}".format(destination, codec))
            ui.notify("Finished Downloading - \"{0}\"".format(folderName), type='positive')



        # Start GUI components
        with ui.column().classes('w-full items-center'):
            ui.label("NewPipe Playlist Extractor").style('color: #ff2d00; font-size: 200%; font-weight: 300')
        with ui.column().classes('w-full items-center'):
            ui.html("Upload NewPipe ZIP file")
            uploadContent = ui.upload(on_upload=handle_upload).props('accept=.zip').classes('max-w-full')


        

        gridPlaylist = ui.aggrid({
        'defaultColDef': {'flex': 1},
        'columnDefs' : [{'headerName': 'Playlist', 'field' : 'playlist',  'filter': 'agTextColumnFilter', 'floatingFilter': True, 'checkboxSelection': True},
        {'headerName': 'Track Count', 'field' : 'count', 'filter': 'agTextColumnFilter', 'floatingFilter': True},],
        'rowData' : [{'playlist' : playlist, 'count' : len(playlists[playlist])} for playlist in list(playlists.keys())],
        'rowSelection': 'multiple',
        }).classes('max-h-100').style('height: 20vw;')

        with ui.row():
            ui.button('Select all', on_click=lambda: gridPlaylist.run_grid_method('selectAll'))  
            ui.button('Deselect all', on_click=lambda: gridPlaylist.run_grid_method('deselectAll')) 

        

        with ui.column().classes('w-full items-center'):
            ui.html("Choose Audio Codec")
            codecChoice = ui.toggle({1: 'MP3', 2: 'WAV', 3: 'FLAC', 4: "ACC", 5 : "OPUS", 6 : "MP4"}, value=1)
            ui.html(" ")
            ui.button('Download Selected Playlists', on_click=lambda: download_selected_rows(), color="green")
        
        with ui.column().classes('w-full items-left'):
            dark = ui.dark_mode(value=True)
            ui.switch('Dark mode', on_change=handle_theme_change).bind_value(dark)
        

        ui.label("============[LOG]============").style('color: #ff2d00; font-size: 100%; font-weight: 300')

    # start GUI and open browser window        
    ui.run()
   
if __name__ in {"__main__", "__mp_main__"}:
        main()


