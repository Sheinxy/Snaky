import commands
import datetime
import discord
import emotes
import json
import os
import random

Client = discord.Client()
token = ''
prefix = '-'


@Client.event
async def on_ready():
    activity = discord.Game(random.choice(["on %s servers" % len(Client.guilds),
                                           "type - or mention me with a command!",
                                           "I'm a robot snake ^w^"]))
    await Client.change_presence(activity=activity, status=discord.Status.idle)
    await writeLog("Logged as %s\nId is: %s" % (Client.user.name, Client.user.id))


@Client.event
async def on_message(message):
    try:
        server = message.guild if message.guild != None else message.author
        channel = message.channel if message.guild != None else message.author
        author = message.author

        if message.content.startswith(prefix) or message.content.startswith('%s ' % Client.user.mention):
            activity = discord.Game(random.choice(["on %s servers" % len(Client.guilds),
                                                   "type - or mention me with a command!",
                                                   "I'm a robot snake ^w^"]))
            await Client.change_presence(activity=activity, status=discord.Status.idle)

            setServerLog = await setServer(server)
            await writeLog("I've received a message from: " + str(author) +
                           "\nOn server: " + server.name + " of ID: " + str(server.id) +
                           "\nOn channel: " + channel.name + " of ID: " + str(channel.id) +
                           "\nMessage's content is: " + message.content +
                           "\n" + setServerLog)

            processCommandLog = await processCommand(message)

            await writeLog(processCommandLog)
    except Exception as e:
        await writeLog("\nSomething went wrong (%s) ;W;" % e)


# @Client.event
# async def on_error(event, *args, **kwargs):
#     await writeLog("Ouch, something went very wrong ;w;")


async def processCommand(message):
    """This function processes any message that might contain a command.
    If the message contains a command, it will be executed.
    The function returns the log, describing what happened.
    """
    server = message.guild if message.guild != None else message.author
    usedPrefix = prefix
    if message.content.startswith('<@%s> ' % Client.user.id):
        usedPrefix = ('<@%s> ' % Client.user.id)

    command = message.content.replace(usedPrefix, "").split(' ')[0]
    arguments = message.content.replace(usedPrefix + command + ' ', ''
                                        ).replace(usedPrefix + command, '')
    serverEmotes = await emotes.loadEmotes(server)
    userEmotes = {}
    if os.path.isfile("Servers/" + str(message.author.id) + "_usr/emotes.json"):
        userEmotes = await emotes.loadEmotes(message.author)

    log = ("The command is: " + command +
           "\nThe arguments are: " + arguments)

    if commands.commands.__contains__(command):
        log += "\nI'm going to execute this command with these arguments\n"
        log += await commands.commands[command](message, arguments)
    elif serverEmotes.__contains__(command):
        log += "\nThis command is an emote"
        log += await emotes.sendEmote(serverEmotes[command], message, arguments)
    elif userEmotes.__contains__(command):
        log += "\nThis command is an emote"
        log += await emotes.sendEmote(userEmotes[command], message, arguments)
    else:
        log += "\nUnknown command"

    return log


async def writeLog(log):
    print("[Debug log, time:", str(datetime.datetime.now()) + "]")
    print(log)
    print("-" * 25)


async def setServer(server):
    """This function checks if a server is currently known and set to the bot.
    If not, it will automatically do it .
    This returns the log, describing what happened.
    """

    serverFolder = "Servers/" + str(server.id) + ("_usr" if (
        type(server) is discord.User or type(server) is discord.Member) else '') + "/"
    log = await setServerFolder(serverFolder)
    log += await setServerEmotes(serverFolder)

    return log


async def setServerFolder(serverFolder):
    log = "\nI'm checking if server is known..."
    if not os.path.isdir(serverFolder):
        log += "\nServer is unknown from me"
        log += "\nI'm creating directory for it"
        os.makedirs(serverFolder)
    else:
        log += "\nServer is known from me, I don't need to create anything"

    return log


async def setServerEmotes(serverFolder):
    log = "\nI'm checking if server is correctly set..."
    if not os.path.isfile(serverFolder + "emotes.json"):
        log += "\nServer is unknown from me"
        log += "\nI'm creating directory for it"
        baseEmotes = {
            "sleep": {
                "title": "$Author(name) went to sleep",
                "description": "Good night $Author(mention)",
                "image": {
                    "url": "$Gif(anime sleep)"
                }
            },
            "kiss": {
                "description": "$Author(mention) kissed $Arguments(all)",
                "image": {
                    "url": "$Gif(anime kiss)"
                }
            },
            "hug": {
                "description": "$Author(mention) hugged $Arguments(all)",
                "image": {
                    "url": "$Gif(anime hug)"
                }
            },
            "eat": {
                "description": "$Author(mention) is going to eat $Arguments(all)",
                "image": {
                    "url": "$Gif(anime eat)"
                }
            },
            "cry": {
                "description": "$Author(mention) is crying",
                "image": {
                    "url": "$Gif(anime cry)"
                }
            },
            "nuke": {
                "description": "$Author(mention) nuked $Arguments(all) :D",
                "image": {
                    "url": "https://cdn.discordapp.com/attachments/333959605883240448/481588083226050571/telechargement.gif"
                }
            },
            "shoot": {
                "description": "$Author(mention) shot $Arguments(all)",
                "image": {
                    "url": "$Gif(anime shoot fire)"
                }
            }
        }
        with open(serverFolder + "emotes.json", "w") as emoteFile:
            json.dump(baseEmotes, emoteFile, indent=4)
    else:
        log += "\nServer is correctly set, I don't need to create anything"

    return log

Client.run(token)
