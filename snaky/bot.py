import discord
import json
import random
import xmltodict
import tools.parsing as parsing
import snaky.permissions as permissions
from snaky.commands import commands
from snaky.custom_commands import execute_command
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
        command_data["private"] or permissions.check_permission(**command_data))

    if permission:
        activity = discord.Game(random.choice([f"on {len(client.guilds)} guilds",
                                               "type - with a command!",
                                               "I'm a robot snake ^w^"]))
        await client.change_presence(activity=activity, status=discord.Status.idle)

        if command_data["command"] in commands:
            await commands[command_data["command"]](**command_data)
        else:
            await check_custom_command(**command_data)


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


async def check_custom_command(message, arguments, user_folder, guild_folder, command, **kwargs):
    base_commands = database.get_data(
        "guilds/public/commands.json")
    commands = database.get_data(
        f"{user_folder}/commands.json", base_commands)
    guild_commands = database.get_data(
        f"{guild_folder}/commands.json", base_commands)
    commands.update(guild_commands)

    if command in commands:
        custom_command = commands[command]
        if "nsfw" in custom_command and custom_command["nsfw"] and not message.channel.nsfw:
            await message.channel.send("This channel isn't nsfw, I'm not a naughty snake, I won't do anything here! >:[")
        elif command in guild_commands or message.author.guild_permissions.external_emojis:
            await execute_command(custom_command, message, arguments, **kwargs)
