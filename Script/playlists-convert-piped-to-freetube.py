#!/usr/bin/env python3

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
        # Create empty Favorites playlist (FreeTube requirement)
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

        # Load Piped JSON data
        with open('playlists-piped.json', 'r', encoding='utf-8') as f:
            piped_data = json.load(f)
        
        # Process each playlist
        for playlist in piped_data.get('playlists', []):
            playlist_name = playlist.get('name', 'Unnamed Playlist')
            video_urls = playlist.get('videos', [])
            
            # Convert URLs to FreeTube format
            ft_playlist = process_playlist(playlist_name, video_urls)
            
            # Write to database
            db.write(json.dumps(ft_playlist, separators=(',', ':')) + '\n')

if __name__ == "__main__":
    main()
