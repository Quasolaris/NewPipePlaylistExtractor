#!/usr/bin/env python3

import ast
import csv
import json
import uuid
import time
from yt_dlp import YoutubeDL

def generate_random_uuid():
    return str(uuid.uuid4())

def get_current_timestamp_ms():
    return int(time.time() * 1000)

def process_video(url):
    opts = {
        'quiet': True,
        'no_warnings': True,
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
    with open('freetube-playlists.db', 'w', encoding='utf-8') as db:
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

        with open('playlists.csv', newline='', encoding='utf-8') as csvfile:
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
                playlist = process_playlist(playlist_name, urls)
                db.write(json.dumps(playlist, separators=(',', ':')) + '\n')

if __name__ == "__main__":
    main()
    