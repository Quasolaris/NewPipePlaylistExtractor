#!/usr/bin/env python3

# playlists-convert-freetube.py
#
# Detects if a playlist row contains a single remote playlist URL.
# Expands that URL using yt_dlp to retrieve all video URLs.
# Converts remote playlist fully into a local playlist with all videos included.
# Finally writes out FreeTube-compatible playlists in freetube-playlists.db.
#
# Usage Example:
# python3 playlists-convert-freetube.py playlists.csv freetube-playlists.db
#
# - The first argument is the input playlists CSV file.
# - The second argument is the output freetube database file.

import ast
import csv
import json
import sys
import uuid
import time
import re
from yt_dlp import YoutubeDL

def generate_random_uuid():
    return str(uuid.uuid4())

def get_current_timestamp_ms():
    return int(time.time() * 1000)

def process_video(url):
    opts = {
        'quiet': True,
        'no_warnings': True
    }
    with YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"Failed to extract info for {url}: {e}")
            return None
        return {
            "videoId": info.get("id"),
            "title": info.get("title"),
            "author": info.get("uploader"),
            "authorId": info.get("channel_id"),
            "lengthSeconds": info.get("duration"),
            "published": int(info.get("timestamp", 0)) * 1000 if info.get("timestamp") else None,
            "timeAdded": get_current_timestamp_ms(),
            "playlistItemId": generate_random_uuid(),
            "type": "video"
        }

def is_remote_playlist(url):
    patterns = [
        r'(?:youtube\.com|youtu\.be).*(list=|/playlist\?id=)',
        r'(?:odysee\.com|odysee\.tv).*/playlist/',
        r'(?:peertube\.)'
    ]
    pattern = re.compile('|'.join(patterns), re.IGNORECASE)
    return bool(pattern.search(url))

def expand_remote_playlist(url):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': True,  # get all entries without downloading
    }
    with YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            entries = info.get('entries', [])
            video_urls = []
            for entry in entries:
                video_url = entry.get('url') or entry.get('webpage_url')
                if video_url:
                    video_urls.append(video_url)
            return video_urls
        except Exception as e:
            print(f"Failed to extract playlist videos from {url}: {e}")
            return []

def process_playlist(playlist_name, urls):
    current_ts = get_current_timestamp_ms()
    _id = "ft-playlist--" + generate_random_uuid()

    videos = []
    for url in urls:
        url = url.strip()
        if url:
            video = process_video(url)
            if video:
                videos.append(video)

    last_updated = max((v["timeAdded"] for v in videos), default=current_ts)

    return {
        "playlistName": playlist_name,
        "protected": False,
        "description": "",
        "videos": videos,
        "_id": _id,
        "createdAt": current_ts,
        "lastUpdatedAt": last_updated
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 playlists-convert-freetube.py playlists.csv freetube-playlists.db")
        sys.exit(1)

    playlists_csv = sys.argv[1]
    freetube_db = sys.argv[2]

    with open(freetube_db, 'w', encoding='utf-8') as db:
        ts = get_current_timestamp_ms()
        favorites = {
            "playlistName": "Favorites",
            "protected": False,
            "description": "Your favorite videos",
            "videos": [],
            "_id": "favorites",
            "createdAt": ts,
            "lastUpdatedAt": ts
        }
        db.write(json.dumps(favorites, separators=(',', ':')) + '\n')

        with open(playlists_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row or not row[0].strip():
                    continue
                playlist_name = row[0].strip().strip('"')
                urls = []
                if len(row) > 1 and row[1].strip():
                    try:
                        urls = ast.literal_eval(row[1].strip())
                    except Exception as e:
                        print(f"Error parsing URLs for playlist {playlist_name}: {e}")
                        urls = []

                # Convert remote playlists into local playlists by expanding URLs
                if len(urls) == 1 and is_remote_playlist(urls[0]):
                    expanded_urls = expand_remote_playlist(urls[0])
                    if expanded_urls:
                        urls = expanded_urls

                playlist = process_playlist(playlist_name, urls)
                db.write(json.dumps(playlist, separators=(',', ':')) + '\n')

if __name__ == "__main__":
    main()
