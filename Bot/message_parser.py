# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to reply to messages
import re
from datetime import datetime, timedelta

import discord

import db_handler
from asynctimer import AsyncTimer

commands = ['yo bot', 'yea bot', 'yea boi']

day_length = 24*60*60


def init(client):
    count = [db_handler.count_song()]

    @client.command(aliases=['hey', 'hi', 'hello'], pass_context=True)
    async def ping(context):
        """Responds with "pong" + a mention to the first username in the arguments if present. Also sends a pm to the
        user using the command."""
        m = context.message
        if m.content.find(" ") > 0:
            user = m.guild.get_member_named(m.content.split(" ")[1])
            await context.send("pong {}".format(user.mention))
        else:
            await context.send("pong")
        await context.message.author.send("pong, but in private.")

    @client.command(pass_context=True)
    async def ban(context):
        """Takes a list of mentioned users + optionally an int. Bans all users in list, and if int has been supplied,
        unbans them after given time in days."""
        m = context.message

        if m.author.guild_permissions.ban_members:
            if m.content.find(" ") > 0:
                try:
                    unban_time = float(m.content.split(" ")[-1])
                except ValueError:
                    unban_time = -1
            else:
                unban_time = -1

            for member in m.mentions:
                await member.ban(delete_message_days=0)
                await context.send("Banned {} for {} days (-1 = indefinite).".format(member.name, unban_time))

            if unban_time >= 0:
                async def unban_all():
                    for member in m.mentions:
                        await m.guild.unban(member)
                        await context.send("unbanned {}.".format(member.name))

                AsyncTimer(unban_time * 86400, unban_all)
        else:
            await context.send("You do not have the permission to ban users")

    @client.command(pass_context=True)
    async def kick(context):
        """Takes a list of mentioned users and kicks them all."""
        m = context.message
        if m.author.guild_permissions.kick_members:
            for member in m.mentions:
                await member.kick()
                await context.send("Kicked {}.".format(member.name))
        else:
            await context.send("You do not have the permission to kick users.")

    @client.command(aliases=['mute', 'silence'], pass_context=True)
    async def timeout(context):
        """Takes a list of mentioned users and a timeout at the end of the message and silences all users for the
        specified time in minutes."""
        m = context.message

        if m.author.guild_permissions.manage_roles:
            muted = discord.utils.get(m.guild.roles, name='Muted')
            if m.content.find(" ") > 0:
                try:
                    mute_time = float(m.content.split(" ")[-1])
                except ValueError:
                    mute_time = -1
            else:
                mute_time = -1

            if mute_time > 0:
                for member in m.mentions:
                    await member.add_roles(muted)
                    await context.send("Muted {} for {} minutes.".format(member.name, int(mute_time)))

                async def unmute_all():
                    for member in m.mentions:
                        await member.remove_roles(muted)
                        await context.send("Unmuted {}.".format(member.name))

                AsyncTimer(mute_time * 60, unmute_all)
            else:
                await context.send("Please provide a time (in minutes).")
        else:
            await context.send("You do not have the permission to ban users.")

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
                    comment = ""
                    pos2 = m.content[pos1:].strip().find(" ")
                    if pos2 > 0:
                        comment = m.content[pos2 + pos1 + 2:].strip()

                    db_handler.add_song_to_queue(url, m.author.name, comment)
                    await context.send("Added!")
                else:
                    await context.send("This song is already submitted!")
            else:
                await context.send("Please provide a valid URL.")
        else:
            await context.send("Please give at least an URL.")

    @client.command(pass_context=True)
    async def set_song_channel(context):
        m = context.message
        if m.author.guild_permissions.administrator:
            if len(m.channel_mentions) > 0:
                db_handler.set_channel(m.channel_mentions[0].id)
                await context.send("Channel {} configured.".format(m.channel_mentions[0].mention))
            else:
                await context.send("Please provide a channel.")
        else:
            await context.send("Insufficient permissions.")

    @client.command(pass_context=True)
    async def force_send(context):
        m = context.message
        if m.author.guild_permissions.administrator:
            await send_song()
        else:
            await context.send("Insufficient permissions.")

    @client.command(aliases=['h' + 'm' * i for i in range(2000)], pass_context=True)
    async def how_many(context):
        m = context.message
        if len(m.mentions) == 0:
            await context.send("{} songs in queue.".format(db_handler.count_song()))
        else:
            for member in m.mentions:
                await context.send("{} has {} songs in queue.".format(member.name, db_handler.count_song(member.name)))

    @client.command(aliases=['ls'], pass_context=True)
    async def list_songs(context):
        await context.send(db_handler.list_songs(context.message.author.name))

    # @client.event
    # async def on_message(message):
    #    """responding to non command messages"""
    #    if message.author != client.user:
    #        if message.channel.name == "bots" and elem_in_string(commands, message.content):
    #            await message.channel.send(random.choice(client.cached_messages).content)
    #    await client.process_commands(message)

    def secs():
        x = datetime.today()
        x_temp = x.replace(hour=12, minute=0, second=0, microsecond=0)
        y = x_temp if x_temp > x else x_temp + timedelta(days=1)
        delta_t = y - x

        return delta_t.seconds + 1

    async def send_song():
        if secs() > 24 * 60 * 60 - 300:
            count[0] = db_handler.count_song()
        song = db_handler.get_song()
        if song is None:
            await db_handler.send_all(client, "No daily song today.")
        else:
            url, author, comment, _ = song
            await db_handler.send_all(client, "Daily song: {}\n Submitted by {}\n{}".format(url, author, comment))
        start_song_timer()

    def start_song_timer():
        c = count[0] // 15 + 1
        s = secs()
        s = s % (24 * 60 * 60 // c)
        print(c, s)
        AsyncTimer(s, send_song)

    start_song_timer()
