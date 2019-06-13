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
        "Gif": getGif
    }

    toSendEmote = copy.deepcopy(emote)
    await replaceMeta(toSendEmote, metaValues)

    toSendEmote["color"] = 9276813
    toSendEmote["author"] = {
        "name": str(message.author),
        "icon_url": str(message.author.avatar_url_as(static_format='png'))
    }

    if ("$Gif(") in emote["image"]["url"]:
        toSendEmote["footer"] = {
            "text": "Powered by https://tenor.com",
            "icon_url": "https://tenor.com/assets/img/favicon/favicon-16x16.png"
        }

    await message.channel.send(embed=discord.Embed.from_dict(toSendEmote))

    return ("\nEmote sent properly! :3")


async def replaceMeta(dic, metaValues):
    for field in dic:
        if type(dic[field]) is dict:
            await replaceMeta(dic[field], metaValues)
        else:
            fieldValue = dic[field].replace(
                '\\(', '&bo;').replace('\\)', '&bc;').replace("\\$", "&ds;")
            for metaValueName in metaValues:
                metaValue = metaValues[metaValueName]
                pattern = ("\\$" + metaValueName + "\\(([^()]*)\\)")
                metaArgs = re.findall(pattern, fieldValue)

                for metaArg in metaArgs:
                    result = ""
                    metaArg = metaArg.replace('&bo;', '(').replace(
                        '&bc;', ')').replace("&ds;", "$")
                    if callable(metaValue):
                        result = str(await metaValue(metaArg))
                    elif type(metaValue) is list:
                        if metaArg == "all":
                            separator = " "
                            result = separator.join(metaValue)
                        else:
                            result = str(metaValue[int(metaArg)])
                    else:
                        result = str(getattr(metaValue, metaArg))
                    fieldValue = fieldValue.replace(
                        "$" + metaValueName + "(" + metaArg + ")", result)

            fieldValue = fieldValue.replace(
                '&bo;', '(').replace('&bc;', ')').replace("&ds;", "$")
            dic[field] = fieldValue


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
