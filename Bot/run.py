# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to start up the bot

import discord
from discord.ext.commands import Bot
from message_parser import init


def runbot(token):
    client = Bot(command_prefix="!")

    init(client)


    client.run(token)
