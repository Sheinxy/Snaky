import discord
import json
import random
import xmltodict
import tools.parsing as parsing
import snaky.permissions as permissions
from snaky.commands import commands
from snaky.meta_parser import MetaParser
from snaky.snaky_data import SnakyData

client = discord.Client()
database = SnakyData("data")
default_prefix = '-'


@client.event
async def on_ready():
    activity = discord.Game(random.choice([f"on {len(client.guilds)} guilds",
                                           "type - with a command!",
                                           "I'm a robot snake ^w^"]))
    await client.change_presence(activity=activity, status=discord.Status.idle)
    print(f"Logged as {client.user.name}\nId is: {client.user.id}")


@client.event
async def on_member_remove(member):
    guild = member.guild
    channel_id = database.get_data(
        f"guilds/{guild.id}/goodbye.json", {"channel": "default"})["channel"]
    if channel_id != "none":
        channel = guild.system_channel if channel_id == "default" else guild.get_channel(
            int(channel_id))
        em = {
            "title": f"{member} has left the guild ;-;",
            "description": f"Good bye {member.display_name}, may your soul rest in peace",
            "thumbnail": {
                "url": str(member.avatar_url_as(static_format='png'))
            }
        }
        await channel.send(embed=discord.Embed.from_dict(em))


@client.event
async def on_member_join(member):
    guild = member.guild
    channel_id = database.get_data(
        f"guilds/{guild.id}/goodbye.json", {"channel": "default"})["channel"]
    if channel_id != "none":
        channel = guild.system_channel if channel_id == "default" else guild.get_channel(
            int(channel_id))
        em = {
            "title": f"{member} has joined the guild :D",
            "description": f"Welcome {member.display_name}, I hope you will like the place ^w^",
            "thumbnail": {
                "url": str(member.avatar_url_as(static_format='png'))
            }
        }
        await channel.send(embed=discord.Embed.from_dict(em))


@client.event
async def on_message(message):
    command_data = process_message(message)
    permission = command_data["is_command"] and (
        command_data["private"] or permissions.check_permission(command_data))

    if permission:
        activity = discord.Game(random.choice([f"on {len(client.guilds)} guilds",
                                               "type - with a command!",
                                               "I'm a robot snake ^w^"]))
        await client.change_presence(activity=activity, status=discord.Status.idle)

        if command_data["command"] in commands:
            await commands[command_data["command"]](command_data)
        else:
            await check_custom_command(command_data)


def process_message(message):
    '''
        Processes the received message:
        Returns a dict indicating if the message is potentially a command,
        with other parameters that will be used when executing the command.
    '''
    guild = message.guild if message.guild != None else message.author
    guild_folder = f"guilds/{guild.id}"
    if message.guild == None:
        guild_folder += "_usr"

    prefixes = database.get_data(guild_folder + "/prefix.json", [])
    prefixes.append(default_prefix)
    prefixes.sort(key=len, reverse=True)

    for prefix in prefixes:
        if message.content.startswith(prefix):
            command = message.content[len(prefix):].split(' ')[0]
            arguments = message.content[len(prefix + command + ' '):]
            return {
                "is_command": True,
                "private": message.guild == None,
                "client": client,
                "prefix": prefix,
                "command": command,
                "arguments": arguments,
                "message": message,
                "guild": guild,
                "guild_folder": guild_folder,
                "user_folder": f"guilds/{message.author.id}_usr"
            }
    return {
        "is_command": False
    }


async def check_custom_command(command_data):
    message = command_data["message"]
    user_folder = command_data["user_folder"]
    guild_folder = command_data["guild_folder"]
    base_commands = database.get_data(
        "guilds/public/commands.json")
    commands = database.get_data(
        f"{user_folder}/commands.json", base_commands)
    guild_commands = database.get_data(
        f"{guild_folder}/commands.json", base_commands)
    commands.update(guild_commands)

    if command_data["command"] in commands:
        custom_command = commands[command_data["command"]]
        if "nsfw" in custom_command and custom_command["nsfw"] and not message.channel.nsfw:
            await message.channel.send("This channel isn't nsfw, I'm not a naughty snake, I won't do anything here! >:[")
        elif command_data["command"] in guild_commands or message.author.guild_permissions.external_emojis:
            parser = MetaParser({
                "Author": command_data["message"].author,
                "Message": command_data["message"],
                "Arguments": command_data["arguments"].split(' '),
                "Gif": MetaParser.get_gif,
                "Mentions": command_data["message"].mentions,
                "Request": MetaParser.get_response,
                "Json": json.loads,
                "Xml": xmltodict.parse,
                "Random": MetaParser.random_number,
                "NoReturn": MetaParser.no_return
            })
            try:
                await send_custom_command(custom_command, command_data, parser)
            except Exception as e:
                error = {
                    "title": type(e).__name__,
                    "description": f"```{e}```"
                }
                await message.channel.send(embed=discord.Embed.from_dict(error))


async def send_custom_command(custom_command, command_data, parser):
    message = command_data["message"]

    if type(custom_command) is str:
        custom_command = parser.parse_item(custom_command)
        if custom_command:
            await message.channel.send(custom_command)
    else:
        custom_command["color"] = 9276813
        custom_command["author"] = {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        }
        if ("image") in custom_command and ("$Gif(") in custom_command["image"]["url"]:
            custom_command["footer"] = {
                "text": "Powered by https://tenor.com",
                "icon_url": "https://tenor.com/assets/img/favicon/favicon-16x16.png"
            }

        before = custom_command.pop("before", None)
        after = custom_command.pop("after", None)
        variables = custom_command.pop("vars", {})

        if before != None:
            await send_custom_command(before, command_data, parser)

        parser.parse_dict(variables)
        for variable in variables:
            parser.meta_tags[variable] = parsing.try_parse_json(variables[variable])[0]

        parser.parse_dict(custom_command)

        if has_content(custom_command):
            await message.channel.send(embed=discord.Embed.from_dict(custom_command))

        if after != None:
            await send_custom_command(after, command_data, parser)


def has_content(command):
    return ("image" in command
            or "title" in command
            or "description" in command
            or "fields" in command
            or "thumbnail" in command
            or "video" in command)
