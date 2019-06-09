# created by Sami Bosch on Friday, 2 November 2018

# This class handles all accesses to db

import json
import os

import discord
import numpy

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


for i in range(len(db['songs'])):
    if len(db['songs'][i]) == 3:
        db['songs'][i].append(1)
write()


def add_song_to_queue(url, author, comment):
    db['songs'].append((url, author, comment, 1))
    write()


def get_song():
    if len(db['songs']) == 0:
        return None
    else:
        prob = [s[3] for s in db['songs']]
        total = sum(prob)
        prob = [p / total for p in prob]
        r = numpy.random.choice(len(db['songs']), replace=False, p=prob)
        e = db['songs'].pop(r)
        for i in range(len(db['songs'])):
            if db['songs'][i][3] < 500:
                db['songs'][i][3] += 1
        write()
        return e


def has_song(url):
    for u, _, _, _ in db['songs']:
        if u == url:
            return True
    return False


def set_server(server, channel):
    db['channels'].append((server, channel))
    write()


def count_song(user=None):
    if user is None:
        return len(db['songs'])
    else:
        c = 0
        for s in db['songs']:
            if s[1] == user:
                c += 1
        print(c)
        return c


def list_songs(user):
    songs = ""
    for s in db['songs']:
        if s[1] == user:
            songs += "<" + s[0] + ">\n"
    return songs.strip()


def get_servers():
    return db['channels']


async def send_all(client, msg):
    for s, ch in get_servers():
        server = client.get_server(id=s)
        channel = discord.utils.get(server.channels, id=ch)
        await client.send_message(channel, msg)
