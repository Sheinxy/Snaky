import asyncio
import discord
import random
import json
import tools.collections as collections
import tools.parsing as parsing
import snaky.permissions as permissions
from snaky.snaky_data import SnakyData
from snaky.custom_commands import execute_command

database = SnakyData("data")


async def help(message, arguments, client, **kwargs):
    em = {
        "title": "Hellow! I'm Snaky, your friendly neighborhood Snake Robot!",
        "description": "Prefix: -\nUse -help (name) to get the usage of a command ! ^w^",
        "url": "https://sheinxy.github.io/projects/Snaky",
        "thumbnail": {
            "url": str(client.user.avatar_url_as(static_format='png'))
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
        ]
    }

    help_file = database.get_data("help.json", {arguments: "undefined ;W;"})
    if arguments in commands:
        docs = collections.get(list(help_file.values()), arguments)
        doc = docs if docs else f"-{arguments} :: undefined ;W;"
        em["fields"].append({
            "name": "<> is for mandatory arguments, () is for optional ones.",
            "value": f"```asciidoc\n===== {arguments} =====\n{doc}```",
            "inline": True
        })
    else:
        for section in help_file:
            em["fields"].append({
                "name": section,
                "value": '\n'.join(f"`{command}`" for command in help_file[section]),
                "inline": True
            })

    await message.channel.send(embed=discord.Embed.from_dict(em))


async def clear(message, arguments, **kwargs):
    if message.channel.permissions_for(message.author).manage_messages:
        try:
            to_clear = int(arguments)
            await message.delete()
            history = await message.channel.history(limit=to_clear).flatten()

            for old_message in history:
                await old_message.delete()

            response = await message.channel.send(f"{message.author.mention} I have cleared {arguments} message(s) (proud of me? :3c)")
            await response.delete(delay=3)
        except:
            await message.channel.send("I'm very sorry, but I wasn't able to clear anything ;W;")
    else:
        await message.channel.send("HEY! YOU CAN'T DO THIS YOU FEOJA >:[")


async def say(message, arguments, **kwargs):
    await message.channel.send(arguments)


async def commands_help(message, arguments, guild_folder, user_folder, **kwargs):
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
            em["fields"][0]["value"] = f"```json\n{json.dumps(commands[arguments], indent=4)}```"
            await message.channel.send(embed=discord.Embed.from_dict(em))
        else:
            await message.channel.send("I am sorry but I can't find any command with this name :c")


async def add_command(message, arguments, guild_folder, **kwargs):
    name = arguments.split(' ')[0]

    if name[-1] == '\n':
        await message.channel.send("Please enter a valid name D:<")
    else:
        command = parsing.try_parse_json(arguments[len(name + ' '):])[0]
        database.set_data(name, command, f"{guild_folder}/commands.json")

        await message.channel.send(f"I've added the command {name} to this guild ! :3")


async def del_command(message, arguments, guild_folder, **kwargs):
    database.del_data(arguments, f"{guild_folder}/commands.json")

    await message.channel.send(f"I've deleted the command {arguments} from this guild ! :3")


async def quote(message, arguments, guild_folder, **kwargs):
    scope = arguments.split(' ')[0]
    if scope == "guild" or scope == "public":
        folder = "guilds/public" if scope == "public" else guild_folder
        quotes = database.get_data(f"{folder}/quotes.json", [])
        if len(quotes) == 0:
            await message.channel.send("Sowwy, but there are no quotes here ;w; (Please add some TwT)")
        else:
            await message.channel.send(random.choice(quotes))
    else:
        await message.channel.send("Sowwy, but this scope is invalid TwT (Please, precise guild or public)")


async def add_quote(message, arguments, guild_folder, **kwargs):
    scope = arguments.split(' ')[0]
    if scope == "guild" or scope == "public":
        quote = arguments[len(scope + ' '):]
        if quote:
            folder = "guilds/public" if scope == "public" else guild_folder
            database.push_data(quote, f"{folder}/quotes.json")

            await message.channel.send(f"Added this quote to the {scope} ! :3c")
        else:
            await message.channel.send("Pwease send a quote TwT")
    else:
        await message.channel.send("Sowwy, but this scope is invalid TwT (Please, precise guild or public)")


async def prefix(message, guild_folder, **kwargs):
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


async def add_prefix(message, arguments, guild_folder, **kwargs):
    database.push_data(arguments, f"{guild_folder}/prefix.json")

    await message.channel.send(f"Added the prefix {arguments} to the guild ! ^w^")


async def del_prefix(message, arguments, guild_folder, **kwargs):
    database.rem_data(arguments, False, f"{guild_folder}/prefix.json")

    await message.channel.send(f"Removed the prefix {arguments} from the guild ! ^w^")


async def goodbye(message, arguments, guild, guild_folder, **kwargs):
    path = f"{guild_folder}/goodbye.json"

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
            channel = collections.find(
                guild.channels, "name", arguments, False)
        if channel == None:
            channel = message.channel
        database.set_data("channel", channel.id if arguments !=
                          "default" else "default", path)
        await message.channel.send(f"I will send a welcome/goodbye message to {channel.mention} when someone joins/leaves ! ^w^")


async def disable(message, **kwargs):
    await message.channel.send(permissions.change_permission("disabled", message, **kwargs))


async def enable(message, **kwargs):
    await message.channel.send(permissions.change_permission("enabled", message, **kwargs))


async def execute(arguments, **kwargs):
    parsed = parsing.try_parse_json(arguments)[0]
    custom_command = parsed if isinstance(parsed, dict) else arguments
    await execute_command(custom_command, arguments=arguments, **kwargs)


commands = {
    'help': help,
    'clear': clear,
    'say': say,
    'goodbye': goodbye,
    'disable': disable,
    'enable': enable,
    'prefix': prefix,
    'add_prefix': add_prefix,
    'del_prefix': del_prefix,
    'commands': commands_help,
    'define': add_command,
    'undefine': del_command,
    'execute': execute,
    'quote': quote,
    'add_quote': add_quote
}
