# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to start up the bot

import discord
from discord.ext.commands import Bot
from message_parser import init
import db_handler


def runbot(token):
    """Initializes the client's command handler and other non command related functionalities."""
    client = Bot(command_prefix="!")

    db_handler.__init__()
    init(client)

    client.run(token)
