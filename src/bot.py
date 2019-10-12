import discord
import random
from src.commands import commands
from src.meta_parser import MetaParser
from src.snaky_data import SnakyData

client = discord.Client()
database = SnakyData("data")
prefix = '-'


@client.event
async def on_ready():
    activity = discord.Game(random.choice(["on %s servers" % len(client.guilds),
                                           "type - with a command!",
                                           "I'm a robot snake ^w^"]))
    await client.change_presence(activity=activity, status=discord.Status.idle)
    print("Logged as %s\nId is: %s" % (client.user.name, client.user.id))


@client.event
async def on_message(message):
    commandData = process_message(message)

    if commandData["isCommand"]:
        activity = discord.Game(random.choice(["on %s servers" % len(client.guilds),
                                               "type - with a command!",
                                               "I'm a robot snake ^w^"]))
        await client.change_presence(activity=activity, status=discord.Status.idle)

        if commandData["command"] in commands:
            await commands[commandData["command"]](commandData)
        else:
            userFolder = commandData["userFolder"]
            serverFolder = commandData["serverFolder"]
            baseEmotes = baseEmotes = database.get_data(
                "servers/public/emotes.json")
            emotes = database.get_data(
                "%s/emotes.json" % userFolder, baseEmotes)
            emotes.update(database.get_data("%s/emotes.json" %
                                            serverFolder, baseEmotes))

            if commandData["command"] in emotes:
                em = emotes[commandData["command"]]
                if "nsfw" in em and em["nsfw"] and not message.channel.nsfw:
                    await message.channel.send("This channel isn't nsfw, I'm not a naughty snake, I won't do anything here! >:[")
                    return
                em["color"] = 9276813
                em["author"] = {
                    "name": str(message.author),
                    "icon_url": str(message.author.avatar_url_as(static_format='png'))
                }
                if ("image") in em and ("$Gif(") in em["image"]["url"]:
                    em["footer"] = {
                        "text": "Powered by https://tenor.com",
                        "icon_url": "https://tenor.com/assets/img/favicon/favicon-16x16.png"
                    }

                parser = MetaParser({
                    "Author": commandData["message"].author,
                    "Arguments": commandData["arguments"].split(' '),
                    "Gif": MetaParser.get_gif,
                    "Mentions": commandData["message"].mentions,
                    "Api": MetaParser.get_api,
                    "Random": MetaParser.random_number
                })
                parser.parseDict(em)
                await message.channel.send(embed=discord.Embed.from_dict(em))


def process_message(message):
    """
        Processes the received message: 
        Returns a dict indicating if the message is potentially a command,
        with other parameters that will be used when executing the command.
    """
    server = message.guild if message.guild != None else message.author
    serverFolder = "servers/" + \
        (str(server.id) if type(server) is discord.Guild else str(server.id) + "_usr")

    prefixes = database.get_data("%s/prefix.json" % serverFolder, [])
    prefixes.append(prefix)
    prefixes.sort(key=len, reverse=True)

    for pref in prefixes:
        if message.content.startswith(pref):
            command = message.content[len(pref):].split(' ')[0]
            arguments = message.content[len(pref + command + ' '):]
            return {
                "isCommand": True,
                "client": client,
                "prefix": pref,
                "command": command,
                "arguments": arguments,
                "message": message,
                "server": server,
                "serverFolder": serverFolder,
                "userFolder": "servers/" + str(message.author.id) + "_usr"
            }
    return {
        "isCommand": False
    }
