#!/usr/bin/env python3

# piped-convert-playlists.py
#
# Reads "playlists" from playlists-piped.json.
# Export local playlists as rows with lists of video URLs in CSV file.
#
# Usage Example:
# python3 piped-convert-playlists.py playlists-piped.json playlists.csv
#
# - The first argument is the input piped json file.
# - The second argument is the output playlists CSV file.

import json
import csv
import sys

def piped_json_to_csv(json_path, csv_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    playlists = data.get("playlists", [])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # No header row, match your preferred CSV style
        for pl in playlists:
            name = pl.get("name", "")
            urls = pl.get("videos", [])
            writer.writerow([name, str(urls)])

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 piped-convert-playlists.py playlists-piped.json playlists.csv")
        sys.exit(1)
    in_json = sys.argv[1]
    out_csv = sys.argv[2]
    piped_json_to_csv(in_json, out_csv)
    print(f"Converted {in_json} to {out_csv}.")

if __name__ == "__main__":
    main()
