#!/usr/bin/env python3

# freetube-convert-playlists.py
#
# Read each playlist line from FreeTube's JSON lines db.
# Extract the video IDs and build YouTube watch URLs.
# Save as CSV with playlist name and a Python list string of URLs.
#
# Usage Example:
# python3 freetube-convert-playlists.py freetube-playlists.db playlists.csv
#
# - The first argument is the input freetube database file.
# - The second argument is the output playlists CSV file.

import json
import csv
import sys

def freetube_to_csv(in_db, out_csv):
    with open(in_db, "r", encoding="utf-8") as f_in, \
         open(out_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        # No header to match CSV format

        for line in f_in:
            line = line.strip()
            if not line:
                continue
            playlist = json.loads(line)
            name = playlist.get("playlistName", "")
            videos = playlist.get("videos", [])
            urls = [video.get("videoId") and f"https://www.youtube.com/watch?v={video.get('videoId')}"
                    for video in videos if video.get("videoId")]

            # Skip empty Favorites or Watch Later playlists
            if name in ("Favorites", "Watch Later") and not urls:
                continue

            # Write playlist name and Python-style list string of video URLs
            writer.writerow([name, str(urls)])

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 freetube-convert-playlists.py freetube-playlists.db playlists.csv")
        sys.exit(1)

    in_db = sys.argv[1]
    out_csv = sys.argv[2]

    freetube_to_csv(in_db, out_csv)
    print(f"Converted {in_db} to {out_csv}.")

if __name__ == "__main__":
    main()
