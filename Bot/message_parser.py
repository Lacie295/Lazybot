# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to reply to messages
import asyncio
import random
import re
from datetime import datetime, timedelta
from math import ceil, floor

import discord
import logging

import db_handler
import logger
from asynctimer import AsyncTimer
from utils import elem_in_string

commands = ['yo bot', 'yea bot', 'yea boi']

day_length = 24*60*60


def init(client):
    client = client

    @client.command(aliases=['hey', 'hi', 'hello'], pass_context=True)
    async def ping(context):
        """Responds with "pong" + a mention to the first username in the arguments if present. Also sends a pm to the
        user using the command."""
        m = context.message
        if m.content.find(" ") > 0:
            user = m.server.get_member_named(m.content.split(" ")[1])
            await client.say("pong {}".format(user.mention))
        else:
            await client.say("pong")
        await client.send_message(context.message.author, "pong, but in private.")

    @client.command(pass_context=True)
    async def ban(context):
        """Takes a list of mentioned users + optionally an int. Bans all users in list, and if int has been supplied,
        unbans them after given time in days."""
        m = context.message

        if m.author.server_permissions.ban_members:
            if m.content.find(" ") > 0:
                try:
                    unban_time = float(m.content.split(" ")[-1])
                except ValueError:
                    unban_time = -1
            else:
                unban_time = -1

            for member in m.mentions:
                await client.ban(member, delete_message_days=0)
                await client.say("Banned {} for {} days (-1 = indefinite).".format(member.name, unban_time))

            if unban_time >= 0:
                async def unban_all():
                    for member in m.mentions:
                        await client.unban(m.server, member)
                        await client.send_message(m.channel, "unbanned {}.".format(member.name))

                AsyncTimer(unban_time * 86400, unban_all)
        else:
            await client.say("You do not have the permission to ban users")

    @client.command(pass_context=True)
    async def kick(context):
        """Takes a list of mentioned users and kicks them all."""
        m = context.message
        if m.author.server_permissions.kick_members:
            for member in m.mentions:
                await client.kick(member)
                await client.say("Kicked {}.".format(member.name))
        else:
            await client.say("You do not have the permission to kick users.")

    @client.command(aliases=['mute', 'silence'], pass_context=True)
    async def timeout(context):
        """Takes a list of mentioned users and a timeout at the end of the message and silences all users for the
        specified time in minutes."""
        m = context.message

        if m.author.server_permissions.manage_roles:
            muted = discord.utils.get(m.server.roles, name='Muted')
            if m.content.find(" ") > 0:
                try:
                    mute_time = float(m.content.split(" ")[-1])
                except ValueError:
                    mute_time = -1
            else:
                mute_time = -1

            if mute_time > 0:
                for member in m.mentions:
                    await client.add_roles(member, muted)
                    await client.say("Muted {} for {} minutes.".format(member.name, int(mute_time)))

                async def unmute_all():
                    for member in m.mentions:
                        await client.remove_roles(member, muted)
                        await client.send_message(m.channel, "Unmuted {}.".format(member.name))

                AsyncTimer(mute_time * 60, unmute_all)
            else:
                await client.say("Please provide a time (in minutes).")
        else:
            await client.say("You do not have the permission to ban users.")

    @client.command(aliases=['qs'], pass_context=True)
    async def queue_song(context):
        m = context.message
        pos1 = m.content.find(" ")
        if pos1 > 0:
            url = m.content.split(" ")[1]
            regex = re.compile(
                r'^(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if re.match(regex, url) is not None:
                if not db_handler.has_song(url):
                    if db_handler.count_song(m.author.name) < 20:
                        comment = ""
                        pos2 = m.content[pos1:].strip().find(" ")
                        if pos2 > 0:
                            comment = m.content[pos2 + pos1 + 2:].strip()

                        db_handler.add_song_to_queue(url, m.author.name, comment)
                        await client.say("Added!")
                    else:
                        await client.say("You have exceeded the song cap.")
                else:
                    await client.say("This song is already submitted!")
            else:
                await client.say("Please provide a valid URL.")
        else:
            await client.say("Please give at least an URL.")

    @client.command(pass_context=True)
    async def set_song_channel(context):
        m = context.message
        if m.author.server_permissions.administrator:
            if len(m.channel_mentions) > 0:
                print(m.channel_mentions)
                db_handler.set_server(m.server.id, m.channel_mentions[0].id)
                await client.say("Channel {} configured.".format(m.channel_mentions[0].mention))
            else:
                await client.say("Please provide a channel.")
        else:
            await client.say("Insufficient permissions.")

    @client.command(pass_context=True)
    async def force_send(context):
        m = context.message
        if m.author.server_permissions.administrator:
            await send_song(False)
        else:
            await client.say("Insufficient permissions.")

    @client.command(aliases=['hm', 'hmmmmmmmm'], pass_context=True)
    async def how_many(context):
        m = context.message
        if len(m.mentions) == 0:
            await client.say("{} songs in queue.".format(db_handler.count_song()))
        else:
            for member in m.mentions:
                await client.say("{} has {} songs in queue.".format(member.name, db_handler.count_song(member.name)))

    @client.command(aliases=['ls'], pass_context=True)
    async def list_songs(context):
        await client.say(db_handler.list_songs(context.message.author.name))

    @client.event
    async def on_message(message):
        """responding to non command messages"""
        if message.author != client.user:
            if message.channel.name == "bots" and elem_in_string(commands, message.content):
                await client.send_message(message.channel,
                                          client.messages[random.choice(range(len(client.messages)))].content)

        await client.process_commands(message)

    def secs():
        x = datetime.today()
        x_temp = x.replace(hour=12, minute=0, second=0, microsecond=0)
        y = x_temp if x_temp > x else x_temp + timedelta(days=1)
        delta_t = y - x

        cnt = ceil(db_handler.count_song() / 15)
        interval = day_length / cnt
        cnt = ceil(delta_t.seconds / interval)
        next_song = delta_t.seconds - (cnt - 1) * interval

        return delta_t.seconds + 1, cnt, interval, next_song

    async def send_song(timer=True):
        s, c, i, n = secs()
        print(secs())

        if timer:
            AsyncTimer(s, send_song)
            await asyncio.sleep(n)
        for _ in range(c):
            print(secs())
            song = db_handler.get_song()
            if song is None:
                logger.info("not sending song")
                await db_handler.send_all(client, "No daily song today. :(")
                break
            url, author, comment, _ = song
            logger.info("sending song")
            await db_handler.send_all(client, "Daily song: {}\n Submitted by {}\n{}".format(url, author, comment))
            if timer:
                await asyncio.sleep(i)

    AsyncTimer(0, send_song)
