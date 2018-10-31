# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to start up the bot

import discord
from message import respond


def runbot(token):
    client = discord.Client()

    @client.event
    async def on_message(message):
        await respond(message, client)

    client.run(token)
