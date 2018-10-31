# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to reply to messages

import discord


async def respond(message, client):
    if message.author != client.user:
        await client.send_message(message.author, "hoi scrub")
        await client.send_message(message.channel, "hoi there")
