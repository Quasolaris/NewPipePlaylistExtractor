#!/usr/bin/env python3

# newpipe-convert-playlists.py
#
# Convert NewPipe newpipe.db or backup zip to a CSV, each row being a playlist and a list of its video URLs.
# Supports local and remote playlists
#
# Usage Example:
#   python3 newpipe-convert-playlists.py newpipe.db playlists.csv
#   python3 newpipe-convert-playlists.py NewPipeData.zip playlists.csv
#
# - The first argument is the path to your NewPipe database file (newpipe.db or ZIP backup).
# - The second argument is the destination CSV file.

import csv
import os
import sqlite3
import sys
import tempfile
import zipfile

def extract_newpipe_db(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extract('newpipe.db', path=extract_dir)
    return os.path.join(extract_dir, 'newpipe.db')

def read_playlists_from_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Read local playlists
    c.execute("SELECT uid, name FROM playlists")
    local_playlists = c.fetchall()

    # Read remote playlists
    c.execute("SELECT uid, name, url FROM remote_playlists")
    remote_playlists = c.fetchall()

    playlist_map = {}

    # For local playlists, gather video URLs by joining playlist_stream_join and streams tables
    for uid, name in local_playlists:
        c.execute("""
            SELECT s.url FROM playlist_stream_join psj
            JOIN streams s ON psj.stream_id = s.uid
            WHERE psj.playlist_id = ?
            ORDER BY psj.join_index
        """, (uid,))
        urls = [row[0] for row in c.fetchall()]
        playlist_map[name] = urls

    # For remote playlists, add playlist URL as single item list
    for uid, name, url in remote_playlists:
        playlist_map[name] = [url]

    c.close()
    conn.close()
    return playlist_map

def write_playlists_csv(playlist_map, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for name, urls in playlist_map.items():
            # Write playlist name and stringified list of URLs
            writer.writerow([name, str(urls)])

def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python3 newpipe-convert-playlists.py newpipe.db playlists.csv")
        print("  python3 newpipe-convert-playlists.py NewPipeData.zip playlists.csv")
        sys.exit(1)

    input_path = sys.argv[1]
    output_csv = sys.argv[2]

    if input_path.lower().endswith('.zip'):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = extract_newpipe_db(input_path, tmpdir)
            playlist_map = read_playlists_from_db(db_path)
    else:
        playlist_map = read_playlists_from_db(input_path)

    write_playlists_csv(playlist_map, output_csv)
    print(f"Exported {len(playlist_map)} playlists to {output_csv}")

if __name__ == "__main__":
    main()
