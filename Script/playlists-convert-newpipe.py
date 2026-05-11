#!/usr/bin/env python3

# playlists-convert-newpipe.py
#
# Extract the template zip to a temp directory.
# Reads the playlists.csv with playlist names and video URLs
# Separates local and remote playlists
# Fetches detailed video metadata for each local video URL
# Updates streams, playlists, playlist_stream_join, and remote_playlists tables accordingly
# Packs the updated newpipe.db back with settings and preferences into the output zip
#
# Usage Example:
# python3 playlists-convert-newpipe.py NewPipeData-Zip-Template.zip playlists.csv NewPipeData.zip
#
# - The first argument is the input NewPipeData Template zip file.
# - The second argument is the input playlists csv file.
# - the third argument is the output NewPipeData zip file.

import csv
import ast
import os
import re
import sqlite3
import sys
import tempfile
import zipfile

from yt_dlp import YoutubeDL

REMOTE_PLAYLIST_PATTERNS = [
    r'(?:youtube\.com|youtu\.be).*(list=|/playlist\?list=)',
    r'(?:odysee\.com|odysee\.tv).*/playlist/',
    r'(?:peertube\.)'
]
REMOTE_PLAYLIST_RE = re.compile('|'.join(REMOTE_PLAYLIST_PATTERNS), re.IGNORECASE)

def is_remote_playlist(url):
    return bool(REMOTE_PLAYLIST_RE.search(url))

def fetch_video_metadata(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
        'forcejson': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title') or 'Unknown Title',
                'duration': int(info.get('duration') or 0),
                'uploader': info.get('uploader') or 'Unknown Uploader',
                'uploader_url': info.get('uploader_url') or '',
                'thumbnail_url': info.get('thumbnail') or '',
                'view_count': int(info.get('view_count') or 0),
                'textual_upload_date': '',
                'upload_date': int(info.get('timestamp', 0)) * 1000 if info.get('timestamp') else 0
            }
    except Exception as e:
        print(f"Warning: Could not fetch metadata for {url}: {e}")
        return {
            'title': 'Unknown Title',
            'duration': 0,
            'uploader': 'Unknown Uploader',
            'uploader_url': '',
            'thumbnail_url': '',
            'view_count': 0,
            'textual_upload_date': '',
            'upload_date': 0
        }

def read_playlists_csv(csv_path):
    playlists = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 2:
                continue
            name, urls_raw = row
            try:
                urls = ast.literal_eval(urls_raw)
            except Exception:
                urls = []
            playlists.append((name.strip(), urls))
    return playlists

def get_next_uid(cursor, table):
    cursor.execute(f"SELECT seq FROM sqlite_sequence WHERE name=?", (table,))
    row = cursor.fetchone()
    if row:
        return int(row[0]) + 1
    else:
        return 1

def modify_newpipe_db(db_path, playlist_data):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("DELETE FROM streams")
    c.execute("DELETE FROM playlist_stream_join")
    c.execute("DELETE FROM playlists")
    c.execute("DELETE FROM remote_playlists")

    next_stream_uid = get_next_uid(c, "streams")
    next_playlist_uid = get_next_uid(c, "playlists")
    next_remote_uid = get_next_uid(c, "remote_playlists")

    stream_url_map = {}

    for name, urls in playlist_data:
        local_urls = [u for u in urls if not is_remote_playlist(u)]
        remote_urls = [u for u in urls if is_remote_playlist(u)]

        if remote_urls and not local_urls:
            for url in remote_urls:
                c.execute(
                    "INSERT INTO remote_playlists (uid, service_id, name, url, thumbnail_url, uploader, display_index, stream_count) VALUES (?, 0, ?, ?, '', '', 0, 0)",
                    (next_remote_uid, name, url)
                )
                next_remote_uid += 1
        elif local_urls:
            c.execute(
                "INSERT INTO playlists (uid, name, is_thumbnail_permanent, thumbnail_stream_id, display_index) VALUES (?, ?, 0, 0, 0)",
                (next_playlist_uid, name)
            )
            playlist_uid = next_playlist_uid
            next_playlist_uid += 1

            for join_index, url in enumerate(local_urls):
                if url not in stream_url_map:
                    meta = fetch_video_metadata(url)
                    c.execute(
                        """INSERT INTO streams
                        (uid, service_id, url, title, stream_type, duration, uploader, uploader_url,
                        thumbnail_url, view_count, textual_upload_date, upload_date, is_upload_date_approximation)
                        VALUES (?, 0, ?, ?, 'VIDEO_STREAM', ?, ?, ?, ?, ?, ?, ?, 1)""",
                        (
                            next_stream_uid, url, meta['title'], meta['duration'], meta['uploader'],
                            meta['uploader_url'], meta['thumbnail_url'], meta['view_count'], meta['textual_upload_date'],
                            meta['upload_date']
                        )
                    )
                    stream_url_map[url] = next_stream_uid
                    next_stream_uid += 1

                stream_uid = stream_url_map[url]
                c.execute(
                    "INSERT INTO playlist_stream_join (playlist_id, stream_id, join_index) VALUES (?, ?, ?)",
                    (playlist_uid, stream_uid, join_index)
                )

            if local_urls:
                c.execute(
                    "UPDATE playlists SET thumbnail_stream_id=? WHERE uid=?",
                    (stream_url_map[local_urls[0]], playlist_uid)
                )

    c.execute("UPDATE sqlite_sequence SET seq=? WHERE name='streams'", (next_stream_uid - 1,))
    c.execute("UPDATE sqlite_sequence SET seq=? WHERE name='playlists'", (next_playlist_uid - 1,))
    c.execute("UPDATE sqlite_sequence SET seq=? WHERE name='remote_playlists'", (next_remote_uid - 1,))

    conn.commit()
    c.close()
    conn.close()  # explicitly close to avoid locking

def extract_modify_repack(template_zip, csv_file, output_zip):
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(template_zip, 'r') as zf:
            zf.extractall(tmpdir)

        db_path = os.path.join(tmpdir, 'newpipe.db')
        pref_path = os.path.join(tmpdir, 'preferences.json')
        settings_path = os.path.join(tmpdir, 'newpipe.settings')

        if not os.path.isfile(db_path) or not os.path.isfile(pref_path):
            print("Template zip must contain newpipe.db and preferences.json")
            sys.exit(1)

        playlist_data = read_playlists_csv(csv_file)
        modify_newpipe_db(db_path, playlist_data)

        with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(db_path, arcname='newpipe.db')
            zf.write(pref_path, arcname='preferences.json')
            if os.path.isfile(settings_path):
                zf.write(settings_path, arcname='newpipe.settings')

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 playlists-convert-newpipe.py NewPipeData-Zip-Template.zip playlists.csv NewPipeData.zip")
        sys.exit(1)

    extract_modify_repack(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"Created {sys.argv[3]} from template {sys.argv[1]} with playlists from {sys.argv[2]}")

if __name__ == "__main__":
    main()
