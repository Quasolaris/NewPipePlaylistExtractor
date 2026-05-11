#!/usr/bin/env python3

# newpipedb-export-csv.py
#
# exports each table in SQLite database file as separate CSV file in output folder
# Connects to the SQLite database file.
# Lists all tables in the database.
# For each table, selects all data and writes it as CSV with column headers.
# Saves each table as a separate CSV file named after the table inside the specified output directory.
#
# usage example: python3 newpipedb-export-csv.py newpipe.db output-csv-folder

import sqlite3
import csv
import os
import sys

def export_sqlite_to_csv(db_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name_tuple in tables:
        table_name = table_name_tuple[0]
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]

        csv_file_path = os.path.join(output_dir, f"{table_name}.csv")
        with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(column_names)  # Write header
            writer.writerows(rows)         # Write data rows

        print(f"Exported table '{table_name}' to {csv_file_path}")

    cursor.close()
    conn.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 newpipedb-export-csv.py <sqlite-db-file> <output-csv-folder>")
        sys.exit(1)

    db_file = sys.argv[1]
    output_dir = sys.argv[2]

    export_sqlite_to_csv(db_file, output_dir)

if __name__ == "__main__":
    main()
