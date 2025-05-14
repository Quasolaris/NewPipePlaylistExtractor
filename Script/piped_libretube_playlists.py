#!/usr/bin/env python3

import csv
import json

def convert_csv_to_json(csv_file, json_file):
    playlists = []

    with open(csv_file, mode='r', encoding='us-ascii') as file:
        reader = csv.reader(file)
        for row in reader:
            name = row[0]
            videos = eval(row[1])  # Convert string representation of list to actual list
            playlists.append({
                "name": name,
                "type": "playlist",
                "visibility": "private",
                "videos": videos
            })

    with open(json_file, mode='w', encoding='us-ascii') as file:
        json.dump({"playlists": playlists}, file, separators=(',', ':'))

# Usage
convert_csv_to_json('playlists.csv', 'piped-playlists.json')