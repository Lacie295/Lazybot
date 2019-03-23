# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to start up the bot
from datetime import datetime

import discord
from discord.ext.commands import Bot

import db_handler
from asynctimer import AsyncTimer
from message_parser import init


def runbot(token):
    """Initializes the client's command handler and other non command related functionalities."""
    client = Bot(command_prefix="!")

    init(client)

    client.run(token)
