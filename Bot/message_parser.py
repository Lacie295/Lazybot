# created by Sami Bosch on Wednesday, 31 October 2018

# This file contains all functions necessary to reply to messages

import discord


def init(client):
    client = client

    @client.command(name='ping',
                    description="ping",
                    brief="pong",
                    aliases=[],
                    pass_context=True)
    async def ping(context):
        await client.say("pong")
        await client.send_message(context.message.author, "pong, but in private")
