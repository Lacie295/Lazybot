# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to reply to messages

import discord


async def respond(message, client):
    if message.author != client.user:
        content = message.content
        if content.startswith('!'):
            print(content)
            if content.find(" ") > 0:
                command = content[1:content.find(" ") + 1]
            else:
                command = content[1:]
            print(command)
            if command == "ping":
                await client.send_message(message.author, "pong")
                await client.send_message(message.channel, "pong")
