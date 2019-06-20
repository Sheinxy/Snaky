import asyncio
import datetime
import discord
import emotes
import json
import os
import random
import rule34 as r34


async def help(message, arguments):
    """Hellow! I'm Snaky, your friendly neighborhood Snake Robot!
    Do you want to know how to use me properly? :3
    """
    em = {
        "title": ("Hellow! I'm Snaky, your friendly neighborhood Snake Robot!"),
        "description": "Prefix: -, but you can also @ me",
        "thumbnail": {
            "url": "https://cdn.discordapp.com/attachments/499994899404554261/588756234992091156/Snaky_v5_No_Sign.png"
        },
        "author": {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        },
        "footer": {
            "text": "Bot creates by https://twitter.com/Sheinxy",
            "icon_url": "https://cdn.discordapp.com/attachments/499994899404554261/588756332765511681/A_Bit_Biceon_More_No_Sign.png"
        },
        "color": 9276813,
        "fields": []
    }
    for commandName in commands:
        doc = commands[commandName].__doc__
        em["fields"].append({
            "name": commandName,
            "value": doc,
            "inline": False
        })

    await message.channel.send(embed=discord.Embed.from_dict(em))


async def clear(message, arguments):
    """I can help clearing your junk!
    Just tell me how many messages I have to delete and I will do it! UwU
    """
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


async def say(message, arguments):
    """I will repeat anything that you say! :3
    Like a small parrot! (But I'm a Snake, so please, don't say that I'm a parrot ;W;)
    """
    await message.channel.send(arguments)


async def ping(message, arguments):
    """Want to know how much latency there is between discord and I?
    I will tell the time between the creation of your message and the moment I received it! :3
    """
    messageCreation = message.created_at
    currentTime = datetime.datetime.now()

    timeDifference = currentTime.__sub__(messageCreation)
    await message.channel.send("Pong (" + str(timeDifference.microseconds / 1000) + "ms approximately)")


async def rule34(message, arguments):
    """Ohh, you want to be nasty uh? >w>
    Want me to call you 'master' as well? owo
    """
    if not message.channel.nsfw:
        await message.channel.send("This channel isn't nsfw, I'm not a naughty snake, I won't do anything here! >:[")

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


async def emotesHelp(message, arguments):
    """I can display so many emotes!
    You must be lost with all of them, let me refresh your memory to help you! :3
    """
    em = {
        "author": {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        },
        "color": 9276813,
        "fields": [
            {
                "name": "This server's emotes are the following:",
                "value": "",
                "inline": False
            }]
    }

    serverEmotes = await emotes.loadEmotes(message.guild if message.guild != None else message.author)

    for emote in serverEmotes:
        em["fields"][0]["value"] += ("`%s` " % emote)

    if message.guild != None and os.path.isfile("Servers/" + str(message.author.id) + "_usr/emotes.json"):
        userEmotes = await emotes.loadEmotes(message.author)
        em["fields"].append({
            "name": "Your custom emotes are the following:",
            "value": "",
            "inline": False
        })
        for emote in userEmotes:
            em["fields"][1]["value"] += ("`%s` " % emote)

    await message.channel.send(embed=discord.Embed.from_dict(em))


async def addEmote(message, arguments):
    """Usage is:
    -addEmote name {"title": "Something", "description": "Something", "image": {"url": "Something"}}
    Meta values [$Name(Arguments)] are: Author, Gif, Arguments
    """
    server = message.guild if message.guild != None else message.author
    name = arguments.split(' ')[0]
    emote = json.loads(arguments.replace(name + ' ', ''))

    await emotes.addEmote(server, name, emote)

    await message.channel.send("I've added the emote " + name + " to this server! :3")


async def delEmote(message, arguments):
    """Are you unsatisfied by an emote?
    I can delete it for you! :3
    """
    await emotes.delEmote((message.guild if message.guild != None else message.author), arguments)

    await message.channel.send("I've deleted the emote " + arguments + " from this server! :3")


commands = {
    'help': help,
    'clear': clear,
    'say': say,
    'ping': ping,
    'rule34': rule34,
    'emotes': emotesHelp,
    'addEmote': addEmote,
    'delEmote': delEmote
}
