#!/usr/bin/env python3

import csv
import json
import ast

def convert_csv_to_piped_json():
    # Initialize playlists list
    playlists = []
    
    # Read CSV file
    with open('playlists.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        for row in csv_reader:
            if len(row) < 2:
                continue  # Skip invalid rows
            
            name = row[0]
            urls_str = row[1]
            
            # Convert string representation of list to actual list
            try:
                url_list = ast.literal_eval(urls_str)
            except (SyntaxError, ValueError):
                continue  # Skip rows with invalid format
            
            # Normalize URLs to youtube.com format
            normalized_urls = [
                url.replace('www.youtube.com', 'youtube.com')
                for url in url_list
            ]
            
            # Create playlist object
            playlist_obj = {
                "name": name,
                "type": "playlist",
                "visibility": "private",
                "videos": normalized_urls
            }
            
            playlists.append(playlist_obj)
    
    # Create final JSON structure
    output = {
        "format": "Piped",
        "version": 1,
        "playlists": playlists
    }
    
    # Write JSON file in single-line format
    with open('playlists-piped.json', 'w', encoding='utf-8') as json_file:
        json.dump(output, json_file, ensure_ascii=False, separators=(',', ':'))

if __name__ == '__main__':
    convert_csv_to_piped_json()
    