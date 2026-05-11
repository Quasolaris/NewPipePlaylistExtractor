#!/usr/bin/env python3

# playlists-convert-piped.py
#
# Reads your playlist CSV where each playlist has a list (including remote playlist URLs).
# Expands any remote playlist URLs inside CSV’s playlist lists into video URLs.
# Exports them all as playlists with "type": "playlist" and "visibility": "private".
# Outputs the entire JSON export as one single line.
# Piped does not support importing remote playlists as bookmarks.
# Outputs valid playlists-piped.json for Piped import/export.
#
# Usage Example:
# python3 playlists-convert-piped.py playlists.csv playlists-piped.json
#
# - The first argument is the input playlists CSV file.
# - The second argument is the output piped json file.

import csv
import json
import sys
import ast
import re
from yt_dlp import YoutubeDL

REMOTE_PLAYLIST_PATTERNS = [
    r'(?:youtube\.com|youtu\.be).*(list=|/playlist\?id=)',
    r'(?:odysee\.com|odysee\.tv).*/playlist/',
    r'(?:peertube\.)'
]

REMOTE_PLAYLIST_RE = re.compile('|'.join(REMOTE_PLAYLIST_PATTERNS), re.IGNORECASE)

def is_remote_url(url):
    return bool(REMOTE_PLAYLIST_RE.search(url))

def expand_remote_playlist(url):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': True,
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
            print(f"Failed to expand remote playlist {url}: {e}")
            return []

def read_playlists_csv(csv_file):
    playlists = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 2:
                continue
            name, urls_str = row
            try:
                urls = ast.literal_eval(urls_str)
                if not isinstance(urls, list) or not urls:
                    continue
            except:
                continue

            # Expand remote playlist URLs into local video URLs
            expanded_urls = []
            for url in urls:
                if is_remote_url(url):
                    expanded = expand_remote_playlist(url)
                    if expanded:
                        expanded_urls.extend(expanded)
                    else:
                        expanded_urls.append(url)
                else:
                    expanded_urls.append(url)

            # Remove duplicates and empty
            cleaned_urls = list(dict.fromkeys([u.strip() for u in expanded_urls if u.strip()]))

            playlists.append({
                "name": name.strip(),
                "type": "playlist",
                "visibility": "private",
                "videos": cleaned_urls
            })
    return playlists

def main():
    if len(sys.argv) < 3:
        print("Usage: python playlists-convert-piped.py playlists.csv playlists-piped.json")
        sys.exit(1)

    in_csv = sys.argv[1]
    out_json = sys.argv[2]

    playlists = read_playlists_csv(in_csv)

    piped_data = {
        "format": "Piped",
        "version": 1,
        "playlists": playlists
    }

    # Dump JSON on a single line
    with open(out_json, "w", encoding="utf-8") as jsonf:
        jsonf.write(json.dumps(piped_data, separators=(',', ':')))

    print(f"Exported {len(playlists)} playlists to {out_json}")

if __name__ == "__main__":
    main()
