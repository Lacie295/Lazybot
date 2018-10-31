# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to reply to messages

import discord


def init(client):
    client = client

    @client.command(aliases=['hey', 'hi', 'hello'], pass_context=True)
    async def ping(context):
        await client.say("pong")
        await client.send_message(context.message.author, "pong, but in private")

    @client.command(pass_context=True)
    async def ban(context):
        m = context.message
        if m.author.server_permissions.ban_members:
            for member in m.mentions:
                await client.ban(member, delete_message_days=0)
                await client.say("banned {}".format(member.name))
        else:
            await client.say("you do not have the permission to ban users")

    @client.command(pass_context=True)
    async def kick(context):
        m = context.message
        if m.author.server_permissions.kick_members:
            for member in m.mentions:
                await client.kick(member)
                await client.say("kicked {}".format(member.name))
        else:
            await client.say("you do not have the permission to kick users")
