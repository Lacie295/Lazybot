# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to reply to messages
import asyncio
import re
from datetime import datetime, timedelta

import discord
import random

from discord import PartialEmoji

import db_handler
from asynctimer import AsyncTimer
import sys

queue = {}


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
        split = m.content.split(" ")
        if len(split) > 0:
            regex = re.compile(
                r'^(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            i = 1
            while i < len(split):
                url = split[i]
                if re.match(regex, url):
                    comment = ""
                    while i + 1 < len(split) and not re.match(regex, split[i + 1]):
                        comment += split[i + 1] + " "
                        i += 1
                    comment = comment.strip()
                    if not db_handler.has_song(url):
                        db_handler.add_song_to_queue(url, m.author.name, comment)
                        await context.send(
                            "Added <{}>! Comment: {}".format(url, comment if len(comment) > 0 else "None"))
                    else:
                        await context.send("<{}> is already submitted!".format(url))
                else:
                    await context.send("{} is not a valid URL.".format(url))
                i += 1
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
            await send_song(True)
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

    @client.command(pass_context=True)
    async def exclude_channel(context):
        m = context.message
        if m.author.guild_permissions.administrator:
            if len(m.channel_mentions) > 0:
                for ch in m.channel_mentions:
                    db_handler.exclude_channel(ch.id)
                    await context.send("Excluded {}".format(ch.mention))
            else:
                await context.send("Please provide a channel")
        else:
            await context.send("Insufficient permissions.")

    @client.command(pass_context=True)
    async def allow_channel(context):
        m = context.message
        if m.author.guild_permissions.administrator:
            if len(m.channel_mentions) > 0:
                for ch in m.channel_mentions:
                    db_handler.enable_channel(ch.id)
                    await context.send("Enabled {}".format(ch.mention))
            else:
                await context.send("Please provide a channel")
        else:
            await context.send("Insufficient permissions.")

    @client.command(pass_context=True)
    async def list_excluded(context):
        m = context.message
        if m.author.guild_permissions.administrator:
            s = "\n".join([client.get_channel(ch).mention for ch in db_handler.get_excluded()])
            await context.send(s)
        else:
            await context.send("Insufficient permissions.")

    @client.command(pass_context=True)
    async def set_pin_channel(context):
        """Takes a channel reference and sets it as the default channel to post pins to."""
        m = context.message

        if m.author.guild_permissions.administrator:
            if m.channel_mentions:
                channel = m.channel_mentions[0]
                db_handler.set_pin_channel(channel.id)
                await context.send("Pin channel set to {}".format(channel.name))
            else:
                await context.send("Please provide a channel.")
        else:
            await context.send("You do not have permission to set channels.")

    @client.command(pass_context=True)
    async def set_pin_emote(context):
        """Takes an emote and sets it as the default emote to check for pins."""
        m = context.message

        if m.author.guild_permissions.administrator:
            split = m.content.split(" ")
            if len(split) == 2:
                text = split[1]
                if re.match(r"^<:\w+:\d+>$", text):
                    emoji_id = int(text.split(":")[2][:-1])
                    db_handler.set_pin_emote(emoji_id)
                    emoji = client.get_emoji(emoji_id)
                    print(emoji.name)
                    await m.add_reaction(emoji)
                    await context.send("Emoji <:{}:{}> set as default.".format(emoji.name, emoji.id))
                elif text == "default":
                    db_handler.set_pin_emote("⭐")
                    await m.add_reaction("⭐")
                    await context.send("Emoji ⭐ set as default.")
                else:
                    await context.send("Please provide a valid emote.")
            else:
                await context.send("Please provide an emote.")
        else:
            await context.send("You do not have permission to set emotes.")

    @client.command(pass_context=True)
    async def set_pin_number(context):
        """Sets the amount of emotes required for a message to be pinned."""
        m = context.message

        if m.author.guild_permissions.administrator:
            split = m.content.split(" ")
            if len(split) == 2:
                text = split[1]
                if re.match(r"\d+$", text):
                    db_handler.set_pin_amount(int(text))
                    await context.send("Emotes required for a message to be pinned set to {}.".format(text))
                else:
                    await context.send("Please provide a valid number.")
            else:
                await context.send("Please provide a number.")
        else:
            await context.send("You do not have permission to set channels.")

    @client.event
    async def on_message(message):
        """responding to non command messages"""
        if not message.content.startswith("!") and message.author != client.user and \
                message.channel.id not in db_handler.get_excluded():
            r = random.randint(0, 255)
            print(r)
            if client.user in message.mentions or r < 20:
                await asyncio.sleep(random.randint(0, 255)/100.0)
                async with message.channel.typing():
                    m = random.choice([cm for cm in client.cached_messages if
                                       cm.channel.id not in db_handler.get_excluded()
                                       and isinstance(cm.channel, discord.channel.TextChannel)
                                       and client.user not in cm.mentions
                                       and cm.author != client.user])
                    await asyncio.sleep(len(m.clean_content) * 0.2)
                    print(m)
                    await message.channel.send(m.clean_content, files=[await a.to_file() for a in m.attachments])
        sys.stdout.flush()
        await client.process_commands(message)

    def secs():
        x = datetime.today()
        x_temp = x.replace(hour=12, minute=0, second=0, microsecond=0)
        y = x_temp if x_temp > x else x_temp + timedelta(days=1)
        delta_t = y - x

        return delta_t.seconds

    async def send_song(force=False):
        if secs() > 24 * 60 * 60 - 300:
            count[0] = db_handler.count_song()
        song = db_handler.get_song()
        if song is None:
            await db_handler.send_all(client, "No daily song today.")
        else:
            url, author, comment, _ = song
            await db_handler.send_all(client, "Daily song: {}\n Submitted by {}\n{}".format(url, author, comment))
        if not force:
            start_song_timer()

    def start_song_timer():
        c = count[0] // 15 + 1
        s = secs()
        s = (s % (24 * 60 * 60 / c)) + 1
        print(c, s)
        sys.stdout.flush()
        AsyncTimer(s, send_song)

    start_song_timer()

    @client.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == client.user.id or payload.channel_id == db_handler.get_pin_channel():
            pass
        else:
            m = payload.message_id
            event = asyncio.Event()
            while m in queue:
                await queue[m].wait()

            queue[m] = event
            guild = client.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            member = guild.get_member(payload.user_id)

            pin = False

            ok_emote = 693404150662430750

            print(client.get_emoji(ok_emote))
            sys.stdout.flush()

            if payload.emoji.is_custom_emoji() and payload.emoji.id == ok_emote:
                if member.guild_permissions.manage_messages:
                    pin = True

            for reaction in message.reactions:
                emoji = reaction.emoji
                if not isinstance(emoji, str) and emoji.id == ok_emote:
                    users = await reaction.users().flatten()
                    if client.user in users:
                        pin = False
                        break
                elif isinstance(db_handler.get_pin_emote(), int) and not isinstance(emoji, str) and\
                        emoji.id == db_handler.get_pin_emote() and reaction.count >= db_handler.get_pin_amount():
                    pin = True
                elif (emoji == db_handler.get_pin_emote() or (isinstance(emoji, PartialEmoji)
                                                              and emoji.name == db_handler.get_pin_emote()))\
                        and reaction.count >= db_handler.get_pin_amount():
                    pin = True

            if pin:
                pin_channel = client.get_channel(db_handler.get_pin_channel())
                await pin_channel.send(message.clean_content, files=[await a.to_file() for a in message.attachments])
                await message.add_reaction(client.get_emoji(ok_emote))

            event.set()
            queue.pop(m)
