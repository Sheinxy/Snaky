import copy
import discord
import json
import random
import re
import urllib


async def loadEmotes(server):
    emoteFilePath = "Servers/" + str(server.id) + ("_usr" if (type(
        server) is discord.User or type(server) is discord.Member) else '') + "/emotes.json"
    emotes = {}

    with open(emoteFilePath) as emoteFile:
        emotes = json.load(emoteFile)

    return emotes


async def addEmote(server, name, emote):
    emoteFilePath = "Servers/" + str(server.id) + ("_usr" if (type(
        server) is discord.User or type(server) is discord.Member) else '') + "/emotes.json"

    emoteList = await loadEmotes(server)
    emoteList[name] = emote

    with open(emoteFilePath, 'w') as emoteFile:
        json.dump(emoteList, emoteFile, indent=4)


async def delEmote(server, name):
    emoteFilePath = "Servers/" + str(server.id) + ("_usr" if (type(
        server) is discord.User or type(server) is discord.Member) else '') + "/emotes.json"

    emoteList = await loadEmotes(server)
    del emoteList[name]

    with open(emoteFilePath, 'w') as emoteFile:
        json.dump(emoteList, emoteFile, indent=4)


async def sendEmote(emote, message, arguments):
    metaValues = {
        "Author": message.author,
        "Arguments": arguments.split(' '),
        "Gif": getGif,
        "Mentions": message.mentions
    }

    toSendEmote = copy.deepcopy(emote)
    await replaceMeta(toSendEmote, metaValues)

    toSendEmote["color"] = 9276813
    toSendEmote["author"] = {
        "name": str(message.author),
        "icon_url": str(message.author.avatar_url_as(static_format='png'))
    }

    if ("image") in emote and ("$Gif(") in emote["image"]["url"]:
        toSendEmote["footer"] = {
            "text": "Powered by https://tenor.com",
            "icon_url": "https://tenor.com/assets/img/favicon/favicon-16x16.png"
        }

    await message.channel.send(embed=discord.Embed.from_dict(toSendEmote))


async def replaceMeta(dic, metaValues):
    async def getMetaResult(meta, metaArgument):
        if callable(meta):
            result = await meta(metaArgument)
        elif type(meta) is list:
            if metaArgument == "all":
                separator = " "
                result = separator.join(map(str, meta))
            else:
                result = meta[int(metaArgument)]
        else:
            result = getattr(meta, metaArgument)

        return result

    async def getMetaArgument(cursor, expression):
        metaArgument = ""
        cursor += 1
        while fieldValue[cursor] != ")":
            metaArgument += fieldValue[cursor]
            cursor += 1
        expression += metaArgument + fieldValue[cursor]

        return [metaArgument, cursor, expression]

    for field in dic:
        if type(dic[field]) is dict:
            await replaceMeta(dic[field], metaValues)
        else:
            cursor = 0
            fieldValue = dic[field]
            while cursor < len(fieldValue):
                if fieldValue[cursor] == "$":
                    expression = fieldValue[cursor]
                    metaValue = ""
                    cursor += 1
                    while fieldValue[cursor] != "(":
                        metaValue += fieldValue[cursor]
                        cursor += 1
                    expression += metaValue + fieldValue[cursor]    
                    metaArgumentRes = await getMetaArgument(cursor, expression)
                    cursor = metaArgumentRes[1]
                    expression = metaArgumentRes[2]
                    if metaValue in metaValues:
                        meta = metaValues[metaValue]
                        result = await getMetaResult(meta, metaArgumentRes[0])
                        cursor += 1
                        while cursor < len(fieldValue) and fieldValue[cursor] == "(":
                            expression += fieldValue[cursor]
                            metaArgumentRes = await getMetaArgument(cursor, expression)
                            cursor = metaArgumentRes[1]
                            expression = metaArgumentRes[2]
                            result = await getMetaResult(result, metaArgumentRes[0])
                            cursor += 1
                            
                        fieldValue = fieldValue.replace(expression, str(result))
                        dic[field] = fieldValue
                        cursor = len(str(result))
                else :
                    cursor += 1


async def getGif(searchQuery):
    gifUrl = "https://media1.tenor.com/images/4cf708c3935a0755bbe1e9d52ef8378d/tenor.gif?itemid=13009757"
    apiKey = "ALP58D29DLCU"
    limit = 50

    requestGifs = urllib.request.urlopen(
        "https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" %
        (searchQuery.replace(' ', '%20'), apiKey, limit))

    requestGifsContent = json.loads(requestGifs.read())

    if requestGifs.code == 200:
        gifUrl = random.choice(requestGifsContent["results"])[
            "media"][0]["gif"]["url"]

    return gifUrl
