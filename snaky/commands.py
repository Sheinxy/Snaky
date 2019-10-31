import asyncio
import discord
import random
import json
import tools.dictionnary as dictionnary
import tools.parsing as parsing
import snaky.permissions as permissions
from snaky.snaky_data import SnakyData
from snaky.custom_commands import execute_command

database = SnakyData("data")


async def help(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]

    em = {
        "title": "Hellow! I'm Snaky, your friendly neighborhood Snake Robot!",
        "description": "Prefix: -\nUse -help (name) to get the usage of a command ! ^w^",
        "url": "https://sheinxy.github.io/projects/Snaky",
        "thumbnail": {
            "url": str(command_data["client"].user.avatar_url_as(static_format='png'))
        },
        "author": {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        },
        "footer": {
            "text": "Bot created by https://sheinxy.github.io",
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
        doc = (
            f"-{arguments} :: undefined ;W;") if not arguments in docs else docs[arguments]
        em["fields"][0]["name"] = "<> is for mandatory arguments, () is for optional ones."
        em["fields"][0]["value"] = (
            f"```asciidoc\n===== {arguments} =====\n{doc}```")
    else:
        for command in commands:
            em["fields"][0]["value"] += f'`{command}` '

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

            response = await message.channel.send(f"{message.author.mention} I have cleared {arguments} message(s) (proud of me? :3c)")
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
    guild_folder = command_data["guild_folder"]
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

        base_commands = database.get_data("guilds/public/commands.json")
        user_commands = database.get_data(
            f"{user_folder}/commands.json", base_commands)
        guild_commands = []
        if guild_folder != user_folder:
            em["fields"].append({
                "name": "This guild's commands are the following:",
                "value": "",
                "inline": False
            })
            guild_commands = database.get_data(
                f"{guild_folder}/commands.json", base_commands)

        for command in user_commands:
            em["fields"][0]["value"] += f"`{command}` "
        for command in guild_commands:
            em["fields"][1]["value"] += f"`{command}` "

        await message.channel.send(embed=discord.Embed.from_dict(em))
    else:
        base_commands = database.get_data(
            "guilds/public/commands.json")
        commands = database.get_data(
            f"{user_folder}/commands.json", base_commands)
        guild_commands = database.get_data(
            f"{guild_folder}/commands.json", base_commands)
        commands.update(guild_commands)

        if arguments in commands:
            em["fields"][0]["name"] = '`' + arguments + '`'
            em["fields"][0]["value"] = (
                f"```json\n{json.dumps(commands[arguments], indent=4)}```")
            await message.channel.send(embed=discord.Embed.from_dict(em))
        else:
            await message.channel.send("I am sorry but I can't find any command with this name :c")


async def add_command(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    name = arguments.split(' ')[0]
    guild_folder = command_data["guild_folder"]
    command = {}
    try:
        command = json.loads(arguments[len(name + ' '):])
    except:
        command = arguments[len(name + ' '):]

    database.set_data(name, command, f"{guild_folder}/commands.json")

    await message.channel.send(f"I've added the command {name} to this guild ! :3")


async def del_command(command_data):
    guild_folder = command_data["guild_folder"]
    arguments = command_data["arguments"]
    message = command_data["message"]

    database.del_data(arguments, f"{guild_folder}/commands.json")

    await message.channel.send(f"I've deleted the command {arguments} from this guild ! :3")


async def quote(command_data):
    message = command_data["message"]
    scope = command_data["arguments"].split(' ')[0]
    if scope == "guild" or scope == "public":
        guild_folder = "guilds/public" if scope == "public" else command_data["guild_folder"]
        quotes = database.get_data(f"{guild_folder}/quotes.json", [])
        if len(quotes) == 0:
            await message.channel.send("Sowwy, but there are no quotes here ;w; (Please add some TwT)")
        else:
            await message.channel.send(random.choice(quotes))
    else:
        await message.channel.send("Sowwy, but this scope is invalid TwT (Please, precise guild or public)")


async def add_quote(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    scope = arguments.split(' ')[0]
    if scope == "guild" or scope == "public":
        quote = arguments[len(scope + ' '):]
        if quote:
            guild_folder = "guilds/public" if scope == "public" else command_data["guild_folder"]
            database.push_data(quote, f"{guild_folder}/quotes.json")

            await message.channel.send(f"Added this quote to the {scope} ! :3c")
        else:
            await message.channel.send("Pwease send a quote TwT")
    else:
        await message.channel.send("Sowwy, but this scope is invalid TwT (Please, precise guild or public)")


async def prefix(command_data):
    message = command_data["message"]
    guild_folder = command_data["guild_folder"]

    prefixes = database.get_data(f"{guild_folder}/prefix.json", [])
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
                    "name": "This guild's prefixes are the following:",
                    "value": "",
                    "inline": False
                }]
        }

        for pref in prefixes:
            em["fields"][0]["value"] += f"`{pref}` "

        await message.channel.send(embed=discord.Embed.from_dict(em))
    else:
        await message.channel.send("Am sowwy, but there are no prefixes here TwT")


async def add_prefix(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    guild_folder = command_data["guild_folder"]

    database.push_data(arguments, f"{guild_folder}/prefix.json")

    await message.channel.send(f"Added the prefix {arguments} to the guild ! ^w^")


async def del_prefix(command_data):
    message = command_data["message"]
    arguments = command_data["arguments"]
    guild_folder = command_data["guild_folder"]

    database.rem_data(arguments, False, f"{guild_folder}/prefix.json")

    await message.channel.send(f"Removed the prefix {arguments} from the guild ! ^w^")


async def goodbye(command_data):
    message = command_data["message"]
    guild = command_data["guild"]
    arguments = command_data["arguments"]
    path = command_data["guild_folder"] + "/goodbye.json"

    if arguments == "none":
        database.set_data("channel", arguments, path)
        await message.channel.send("I will not send any welcome/goodbye message ;w;")
    else:
        parsed = parsing.try_parse_int(arguments)
        channel = None
        if parsed[1]:
            channel_id = parsed[0]
            channel = guild.get_channel(channel_id)
        elif arguments == "default":
            channel = guild.system_channel
        elif len(message.channel_mentions) > 0:
            channel = message.channel_mentions[0]
        else:
            channel = dictionnary.find(
                guild.channels, "name", arguments, False)
        if channel == None:
            channel = message.channel
        database.set_data("channel", channel.id if arguments !=
                          "default" else "default", path)
        await message.channel.send(f"I will send a welcome/goodbye message to {channel.mention} when someone joins/leaves ! ^w^")


async def disable(command_data):
    message = command_data["message"]
    await message.channel.send(permissions.change_permission("disabled", command_data))


async def enable(command_data):
    message = command_data["message"]
    await message.channel.send(permissions.change_permission("enabled", command_data))


async def execute(command_data):
    custom_command = parsing.try_parse_json(command_data["arguments"])[0]
    await execute_command(custom_command, command_data)


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
    "enable": enable,
    "execute": execute
}
