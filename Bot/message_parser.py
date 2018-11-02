# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to reply to messages
import time
import random
import discord

from asynctimer import AsyncTimer
import db_handler


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
        await client.send_message(context.message.author, "pong, but in private")

    @client.command(pass_context=True)
    async def ban(context):
        """Takes a list of mentioned users + optionally an int. Bans all users in list, and if int has been supplied,
        unbans them after given time in days."""
        m = context.message
        if m.content.find(" ") > 0:
            try:
                unban_time = float(m.content.split(" ")[-1])
            except ValueError:
                unban_time = -1
        else:
            unban_time = -1

        if m.author.server_permissions.ban_members:
            for member in m.mentions:
                await client.ban(member, delete_message_days=0)
                await client.say("banned {} for {} days (-1 = indefinite)".format(member.name, unban_time))

            if unban_time >= 0:
                async def unban_all():
                    for member in m.mentions:
                        await client.unban(m.server, member)
                        await client.send_message(m.channel, "unbanned {}".format(member.name))
                t = AsyncTimer(unban_time * 86400, unban_all)
        else:
            await client.say("you do not have the permission to ban users")

    @client.command(pass_context=True)
    async def kick(context):
        """Takes a list of mentioned users and kicks them all."""
        m = context.message
        if m.author.server_permissions.kick_members:
            for member in m.mentions:
                await client.kick(member)
                await client.say("kicked {}".format(member.name))
        else:
            await client.say("you do not have the permission to kick users")

    @client.command(aliases=['mute', 'silence'], pass_context=True)
    async def timeout(context):
        """Takes a list of mentioned users and a timeout at the end of the message and silences all users for the
        specified time in minutes."""
        m = context.message
        muted = discord.utils.get(m.server.roles, name='Muted')
        if m.content.find(" ") > 0:
            try:
                mute_time = float(m.content.split(" ")[-1])
            except ValueError:
                mute_time = -1
        else:
            mute_time = -1

        if m.author.server_permissions.manage_roles and mute_time >= 0:
            for member in m.mentions:
                await client.add_roles(member, muted)
                await client.say("Muted {} for {} minutes".format(member.name, int(mute_time)))
            if mute_time >= 0:
                async def unban_all():
                    for member in m.mentions:
                        await client.remove_roles(member, muted)
                        await client.send_message(m.channel, "Unmuted {}".format(member.name))

                AsyncTimer(mute_time * 60, unban_all)
        elif mute_time == -1:
            await client.say("Please provide a time (in minutes)")
        else:
            await client.say("you do not have the permission to ban users")

    @client.event
    async def on_message(message):
        """responding to non command messages"""
        if message.author != client.user:
            if message.channel.name == "bots" and "yo bot" in message.content:
                await client.send_message(message.channel,
                                          client.messages[random.choice(range(len(client.messages)))].content)
        await client.process_commands(message)
