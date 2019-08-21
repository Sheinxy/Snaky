import asyncio
import discord
import random
import rule34 as r34
import json
from src.snaky_data import SnakyData

database = SnakyData("data")


async def help(commandData):
    message = commandData["message"]
    arguments = commandData["arguments"]

    em = {
        "title": "Hellow! I'm Snaky, your friendly neighborhood Snake Robot!",
        "description": "Prefix: -\nUse -help (command) to get the usage of a command ! ^w^",
        "thumbnail": {
            "url": str(commandData["client"].user.avatar_url_as(static_format='png'))
        },
        "author": {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        },
        "footer": {
            "text": "Bot created by https://twitter.com/Sheinxy",
            "icon_url": "https://www.gravatar.com/avatar/88a7ac03b956d2e189af6b3fa6dc6ebe?s=150"
        },
        "color": 9276813,
        "fields": [
            {
                "name": "Commands are: ",
                "value": "",
                "inline": True
            }
        ]
    }

    if arguments in commands:
        docs = database.get_data("help.json", {arguments: "undefined"})
        doc = ("-%s :: undefined ;W;" %
               arguments) if not arguments in docs else docs[arguments]
        em["fields"][0]["name"] = "<> is for mandatory arguments, () is for optional ones."
        em["fields"][0]["value"] = (
            "```asciidoc\n===== %s =====\n%s```" % (arguments, doc))
    else:
        for command in commands:
            em["fields"][0]["value"] += '`%s` ' % command

    await message.channel.send(embed=discord.Embed.from_dict(em))


async def clear(commandData):
    message = commandData["message"]
    arguments = commandData["arguments"]

    if not message.channel.permissions_for(message.author).manage_messages:
        await message.channel.send("HEY! YOU CAN'T DO THIS YOU FEOJA >:[")
        return
    try:
        toClear = int(arguments)
        await message.delete()
        history = await message.channel.history(limit=toClear).flatten()

        for oldMessage in history:
            await oldMessage.delete()

        response = await message.channel.send(message.author.mention + " I have cleared " + arguments + " message(s) (proud of me? :3c)")
        await response.delete(delay=3)
    except:
        await message.channel.send("I'm very sorry, but I wasn't able to clear anything ;W;")


async def say(commandData):
    message = commandData["message"]
    arguments = commandData["arguments"]
    await message.channel.send(arguments)


async def rule34(commandsData):
    message = commandsData["message"]
    arguments = commandsData["arguments"]

    if not message.channel.nsfw:
        await message.channel.send("This channel isn't nsfw, I'm not a naughty snake, I won't do anything here! >:[")
        return

    Rule34 = r34.Rule34(asyncio.get_event_loop())
    urls = await Rule34.getImageURLS(arguments)
    chosen = random.choice(urls)

    em = {
        "description": ("Rule34 with '%s' as search query for %s" % (arguments, message.author.mention)),
        "image": {
            "url": chosen
        },
        "author": {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        },
        "footer": {
            "text": "Powered by https://github.com/LordOfPolls/Rule34-API-Wrapper and https://rule34.xxx/",
            "icon_url": "https://images-ext-2.discordapp.net/external/W_Wi7zqX1K8P60tLneO5e2B_fxpyCHee04VSrNPuhRY/https/rule34.xxx/images/header2.png"
        },
        "color": 9276813
    }

    await message.channel.send(embed=discord.Embed.from_dict(em))


async def emotesHelp(commandData):
    message = commandData["message"]
    serverFolder = commandData["serverFolder"]
    userFolder = commandData["userFolder"]

    em = {
        "author": {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        },
        "color": 9276813,
        "fields": [
            {
                "name": "Your custom emotes are the following:",
                "value": "",
                "inline": False
            }]
    }

    baseEmotes = database.get_data("servers/public/emotes.json")
    userEmotes = database.get_data("%s/emotes.json" % userFolder, baseEmotes)
    serverEmotes = []
    if serverFolder != userFolder:
        em["fields"].append({
            "name": "This server's emotes are the following:",
            "value": "",
            "inline": False
        })
        serverEmotes = database.get_data(
            "%s/emotes.json" % serverFolder, baseEmotes)

    for emote in userEmotes:
        em["fields"][0]["value"] += ("`%s` " % emote)
    for emote in serverEmotes:
        em["fields"][1]["value"] += ("`%s` " % emote)

    await message.channel.send(embed=discord.Embed.from_dict(em))


async def addEmote(commandData):
    message = commandData["message"]
    arguments = commandData["arguments"]
    name = arguments.split(' ')[0]
    serverFolder = commandData["serverFolder"]
    emote = json.loads(arguments[len(name + ' '):])

    database.set_data(name, emote, "%s/emotes.json" % serverFolder)

    await message.channel.send("I've added the emote " + name + " to this server! :3")


async def delEmote(commandData):
    serverFolder = commandData["serverFolder"]
    arguments = commandData["arguments"]
    message = commandData["message"]

    database.del_data(arguments, "%s/emotes.json" % serverFolder)

    await message.channel.send("I've deleted the emote " + arguments + " from this server! :3")


async def quote(commandData):
    message = commandData["message"]
    scope = commandData["arguments"].split(' ')[0]
    if scope != "server" and scope != "public":
        await message.channel.send("Sowwy, but this scope is invalid TwT (Please, precise server or public)")
        return
    serverFolder = "public" if scope == "public" else commandData["serverFolder"]
    quotes = database.get_data("%s/quotes.json" % serverFolder, [])
    if (len(quotes) == 0):
        await message.channel.send("Sowwy, but there are no quotes here ;w; (Please add some TwT)")
        return

    await message.channel.send(random.choice(quotes))


async def addQuote(commandData):
    """
    """
    message = commandData["message"]
    arguments = commandData["arguments"]
    scope = arguments.split(' ')[0]
    if scope != "server" and scope != "public":
        await message.channel.send("Sowwy, but this scope is invalid TwT (Please, precise server or public)")
        return
    quote = arguments[len(scope + ' '):]
    if (quote == ""):
        await message.channel.send("Pwease send a quote TwT")
        return
    serverFolder = "public" if scope == "public" else commandData["serverFolder"]
    database.push_data(quote, "%s/quotes.json" % serverFolder)

    await message.channel.send("Added this quote to the %s ! :3c" % scope)


async def prefix(commandData):
    message = commandData["message"]
    serverFolder = commandData["serverFolder"]

    prefixes = database.get_data("%s/prefix.json" % serverFolder, [])
    if len(prefixes) == 0:
        await message.channel.send("Am sowwy, but there are no prefixes here TwT")
        return
    prefixes.sort(key=len, reverse=True)

    em = {
        "author": {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        },
        "color": 9276813,
        "fields": [
            {
                "name": "This server's prefixes are the following:",
                "value": "",
                "inline": False
            }]
    }

    for pref in prefixes:
        em["fields"][0]["value"] += ("`%s` " % pref)

    await message.channel.send(embed=discord.Embed.from_dict(em))


async def addPrefix(commandData):
    message = commandData["message"]
    arguments = commandData["arguments"]
    serverFolder = commandData["serverFolder"]

    database.push_data(arguments, "%s/prefix.json" % serverFolder)

    await message.channel.send("Added the prefix %s to the server ! ^w^" % arguments)


async def delPrefix(commandData):
    message = commandData["message"]
    arguments = commandData["arguments"]
    serverFolder = commandData["serverFolder"]

    database.rem_data(arguments, False, "%s/prefix.json" % serverFolder)

    await message.channel.send("Removed the prefix %s from the server ! ^w^" % arguments)

commands = {
    'help': help,
    'clear': clear,
    'say': say,
    'rule34': rule34,
    'emotes': emotesHelp,
    'addEmote': addEmote,
    'delEmote': delEmote,
    'quote': quote,
    'addQuote': addQuote,
    'prefix': prefix,
    'addPrefix': addPrefix,
    'delPrefix': delPrefix
}
