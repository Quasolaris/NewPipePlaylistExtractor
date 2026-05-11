#!/usr/bin/env python3

# grayjay-convert-playlists.py
#
# extracts the zipped GrayJay export
# reads its playlists content and groups videos by playlist name
# writes to CSV matching playlist CSV format
#
# Usage Example:
# python3 grayjay-convert-playlists.py grayjay-export.zip playlists.csv
#
# - The first argument is the input grayjay-export ZIP archive.
# - The second argument is the output playlists CSV file.

import zipfile
import os
import json
import csv
import sys
import tempfile

def grayjay_zip_to_csv(zip_path, csv_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract the zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        # Path to playlists file inside unzipped folder
        playlists_file = os.path.join(tmpdir, "stores", "Playlists")

        # Read playlists entries
        if not os.path.exists(playlists_file):
            print(f"Error: Playlists file {playlists_file} not found in zip")
            return

        with open(playlists_file, "r", encoding="utf-8") as f:
            playlists_data = json.load(f)

        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # No header row for consistency

            # playlists_data is a list of strings each like "playlistname:::uuid\nurl"
            # Group by playlist name into list of URLs
            playlist_map = {}
            for entry in playlists_data:
                try:
                    header, url = entry.split("\n", 1)
                    # header format: playlistname:::uuid
                    playlist_name = header.split(":::")[0]
                    playlist_map.setdefault(playlist_name, []).append(url.strip())
                except Exception as e:
                    print(f"Error parsing entry: {entry}, {e}")
                    continue

            # Write each playlist as: name, Python list string of URLs
            for pname, urls in playlist_map.items():
                writer.writerow([pname, str(urls)])

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 grayjay-convert-playlists.py grayjay-export.zip playlists.csv")
        sys.exit(1)

    zip_path = sys.argv[1]
    csv_path = sys.argv[2]

    grayjay_zip_to_csv(zip_path, csv_path)
    print(f"Converted {zip_path} to {csv_path}")

if __name__ == "__main__":
    main()
