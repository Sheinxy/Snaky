import asyncio
import discord
import random
import json
import snaky.permissions as permissions
from snaky.snaky_data import SnakyData

database = SnakyData("data")


async def help(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]

    em = {
        "title": "Hellow! I'm Snaky, your friendly neighborhood Snake Robot!",
        "description": "Prefix: -\nUse -help (name) to get the usage of a command ! ^w^",
        "thumbnail": {
            "url": str(command_data["client"].user.avatar_url_as(static_format='png'))
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
        docs = database.get_data("help.json", {arguments: "undefined ;W;"})
        doc = ("-%s :: undefined ;W;" %
               arguments) if not arguments in docs else docs[arguments]
        em["fields"][0]["name"] = "<> is for mandatory arguments, () is for optional ones."
        em["fields"][0]["value"] = (
            "```asciidoc\n===== %s =====\n%s```" % (arguments, doc))
    else:
        for command in commands:
            em["fields"][0]["value"] += '`%s` ' % command

    await message.channel.send(embed=discord.Embed.from_dict(em))


async def clear(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]

    if message.channel.permissions_for(message.author).manage_messages:
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
    else:
        await message.channel.send("HEY! YOU CAN'T DO THIS YOU FEOJA >:[")


async def say(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    await message.channel.send(arguments)


async def commands_help(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    server_folder = command_data["server_folder"]
    user_folder = command_data["user_folder"]
    em = {
        "author": {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        },
        "color": 9276813,
        "fields": [{}]
    }
    if arguments == "":
        em["fields"] = [
            {
                "name": "Your custom commands are the following:",
                "value": "",
                "inline": False
            }]

        base_commands = database.get_data("servers/public/commands.json")
        user_commands = database.get_data(
            "%s/commands.json" % user_folder, base_commands)
        server_commands = []
        if server_folder != user_folder:
            em["fields"].append({
                "name": "This server's commands are the following:",
                "value": "",
                "inline": False
            })
            server_commands = database.get_data(
                "%s/commands.json" % server_folder, base_commands)

        for command in user_commands:
            em["fields"][0]["value"] += ("`%s` " % command)
        for command in server_commands:
            em["fields"][1]["value"] += ("`%s` " % command)

        await message.channel.send(embed=discord.Embed.from_dict(em))
    else:
        base_commands = database.get_data(
            "servers/public/commands.json")
        commands = database.get_data(
            "%s/commands.json" % user_folder, base_commands)
        server_commands = database.get_data("%s/commands.json" %
                                            server_folder, base_commands)
        commands.update(server_commands)

        if arguments in commands:
            em["fields"][0]["name"] = '`' + arguments + '`'
            em["fields"][0]["value"] = ("```json\n%s```" % json.dumps(commands[arguments], indent=4))
            await message.channel.send(embed=discord.Embed.from_dict(em))
        else:
            await message.channel.send("I am sorry but I can't find any command with this name :c")


async def add_command(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    name = arguments.split(' ')[0]
    server_folder = command_data["server_folder"]
    command = {}
    try:
        command = json.loads(arguments[len(name + ' '):])
    except:
        command = arguments[len(name + ' '):]

    database.set_data(name, command, "%s/commands.json" % server_folder)

    await message.channel.send("I've added the command " + name + " to this server! :3")


async def del_command(command_data):
    server_folder = command_data["server_folder"]
    arguments = command_data["arguments"]
    message = command_data["message"]

    database.del_data(arguments, "%s/commands.json" % server_folder)

    await message.channel.send("I've deleted the command " + arguments + " from this server! :3")


async def quote(command_data):
    message = command_data["message"]
    scope = command_data["arguments"].split(' ')[0]
    if scope == "server" or scope == "public":
        server_folder = "servers/public" if scope == "public" else command_data["server_folder"]
        quotes = database.get_data("%s/quotes.json" % server_folder, [])
        if len(quotes) == 0:
            await message.channel.send("Sowwy, but there are no quotes here ;w; (Please add some TwT)")
        else:
            await message.channel.send(random.choice(quotes))
    else:
        await message.channel.send("Sowwy, but this scope is invalid TwT (Please, precise server or public)")


async def add_quote(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    scope = arguments.split(' ')[0]
    if scope == "server" or scope == "public":
        quote = arguments[len(scope + ' '):]
        if quote != "":
            server_folder = "servers/public" if scope == "public" else command_data["server_folder"]
            database.push_data(quote, "%s/quotes.json" % server_folder)

            await message.channel.send("Added this quote to the %s ! :3c" % scope)
        else:
            await message.channel.send("Pwease send a quote TwT")
    else:
        await message.channel.send("Sowwy, but this scope is invalid TwT (Please, precise server or public)")


async def prefix(command_data):
    message = command_data["message"]
    server_folder = command_data["server_folder"]

    prefixes = database.get_data("%s/prefix.json" % server_folder, [])
    if len(prefixes) != 0:
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
    else:
        await message.channel.send("Am sowwy, but there are no prefixes here TwT")


async def add_prefix(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    server_folder = command_data["server_folder"]

    database.push_data(arguments, "%s/prefix.json" % server_folder)

    await message.channel.send("Added the prefix %s to the server ! ^w^" % arguments)


async def del_prefix(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    server_folder = command_data["server_folder"]

    database.rem_data(arguments, False, "%s/prefix.json" % server_folder)

    await message.channel.send("Removed the prefix %s from the server ! ^w^" % arguments)


async def goodbye(command_data):
    message = command_data["message"]
    server = command_data["server"]
    arguments = command_data["arguments"]
    path = command_data["server_folder"] + "/goodbye.json"

    if arguments == "default" or arguments == "none":
        database.set_data("channel", arguments, path)
        if arguments == "none":
            await message.channel.send("I will not send any welcome/goodbye message ;w;")
        else:
            await message.channel.send("I will send a welcome/goodbye message to %s when someone joins/leaves ! ^w^" % server.system_channel.mention)
    else:
        try:
            channel_id = int(arguments)
            channel = server.get_channel(channel_id)
            if channel != None:
                database.set_data("channel", channel_id, path)
                await message.channel.send("I will send a welcome/goodbye message to %s when someone joins/leaves ! ^w^" % channel.mention)
            else:
                await message.channel.send("This channel doesn't exist D:<")
        except:
            await message.channel.send("Please send either default, none, or a channelId :c")


async def disable(command_data):
    message = command_data["message"]
    await message.channel.send(permissions.change_permission("disabled", command_data))


async def enable(command_data):
    message = command_data["message"]
    await message.channel.send(permissions.change_permission("enabled", command_data))


commands = {
    'help': help,
    'clear': clear,
    'say': say,
    'commands': commands_help,
    'define': add_command,
    'undefine': del_command,
    'quote': quote,
    'add_quote': add_quote,
    'prefix': prefix,
    'add_prefix': add_prefix,
    'del_prefix': del_prefix,
    "goodbye": goodbye,
    "disable": disable,
    "enable": enable
}
