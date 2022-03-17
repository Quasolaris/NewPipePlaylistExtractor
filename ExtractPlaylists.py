#!/usr/bin/env python3

# code by rachmadaniHaryono, found on comment: https://github.com/TeamNewPipe/NewPipe/issues/1788#issuecomment-500805819


from io import StringIO
from sqlite3 import Error
import csv
import sqlite3
import sys


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None


def get_rows(db_file):
    conn = create_connection(db_file)

    cmds = """
    select 
            url,
            title,
            playlists.name as playlist_name,
    from streams 
    inner join playlist_stream_join on playlist_stream_join.stream_id = streams.uid
    inner join playlists on playlists.uid == playlist_stream_join.playlist_id
    """
    cur = conn.cursor()
    cur.execute(cmds)
    rows = cur.fetchall()
    return rows


def main(db_file):
    rows = get_rows(db_file)
    f = StringIO()
    wr = csv.writer(f)
    wr.writerow([
        'url', 'title', 'playlist_name'])
    for row in rows:
        wr.writerow(row)
    print(f.getvalue())


if __name__ == '__main__':
    main(sys.argv[1])