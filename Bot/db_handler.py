# created by Sami Bosch on Friday, 2 November 2018

# This class handles all accesses to db

import json
import os

songs = '../songlist.json'
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, songs)
if not os.path.exists(filename):
    with open(filename, "w+") as f:
        json.dump({"songs": [], "channels": []}, f)
        f.truncate()
        f.close()

with open(filename, "r+") as f:
    db = json.load(f)
    f.close()

if "songs" not in db:
    db['songs'] = []

if "channels" not in db:
    db['channels'] = []


def write():
    with open(filename, "w+") as file:
        json.dump(db, file)
        file.truncate()
        file.close()


def add_song_to_queue(url, author, comment):
    db['songs'].append((url, author, comment))
    write()


def get_song():
    if len(db['songs']) == 0:
        return None
    else:
        e = db['songs'].pop(0)
        write()
        return e


def set_server(server, channel):
    db['channels'].append((server, channel))
    write()


def get_servers():
    return db['channels']
