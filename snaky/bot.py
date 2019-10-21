import discord
import random
import snaky.permissions as permissions
from snaky.commands import commands
from snaky.meta_parser import MetaParser
from snaky.snaky_data import SnakyData

client = discord.Client()
database = SnakyData("data")
default_prefix = '-'


@client.event
async def on_ready():
    activity = discord.Game(random.choice(["on %s servers" % len(client.guilds),
                                           "type - with a command!",
                                           "I'm a robot snake ^w^"]))
    await client.change_presence(activity=activity, status=discord.Status.idle)
    print("Logged as %s\nId is: %s" % (client.user.name, client.user.id))


@client.event
async def on_member_remove(member):
    server = member.guild
    channel_id = database.get_data(
        "servers/%s/goodbye.json" % str(server.id), {"channel": "default"})["channel"]
    if channel_id != "none":
        channel = server.system_channel if channel_id == "default" else server.get_channel(
            int(channel_id))
        em = {
            "title": "%s has left the server ;-;" % str(member),
            "description": "Good bye %s, may your soul rest in peace" % member.display_name,
            "thumbnail": {
                "url": str(member.avatar_url_as(static_format='png'))
            }
        }
        await channel.send(embed=discord.Embed.from_dict(em))

@client.event
async def on_member_join(member):
    server = member.guild
    channel_id = database.get_data(
        "servers/%s/goodbye.json" % str(server.id), {"channel": "default"})["channel"]
    if channel_id != "none":
        channel = server.system_channel if channel_id == "default" else server.get_channel(
            int(channel_id))
        em = {
            "title": "%s has joined the server :D" % str(member),
            "description": "Welcome %s, I hope you will like the place ^w^" % member.display_name,
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
        activity = discord.Game(random.choice(["on %s servers" % len(client.guilds),
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
    server = message.guild if message.guild != None else message.author
    server_folder = "servers/" + str(server.id)
    if message.guild == None:
        server_folder += "_usr"

    prefixes = database.get_data(server_folder + "/prefix.json", [])
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
                "server": server,
                "server_folder": server_folder,
                "user_folder": "servers/" + str(message.author.id) + "_usr"
            }
    return {
        "is_command": False
    }

async def check_custom_command(command_data):
    message = command_data["message"]
    user_folder = command_data["user_folder"]
    server_folder = command_data["server_folder"]
    base_commands = database.get_data(
        "servers/public/commands.json")
    commands = database.get_data(
        "%s/commands.json" % user_folder, base_commands)
    server_commands = database.get_data("%s/commands.json" %
                                        server_folder, base_commands)
    commands.update(server_commands)

    if command_data["command"] in commands:
        custom_command = commands[command_data["command"]]
        if "nsfw" in custom_command and custom_command["nsfw"] and not message.channel.nsfw:
            await message.channel.send("This channel isn't nsfw, I'm not a naughty snake, I won't do anything here! >:[")
        elif command_data["command"] in server_commands or message.author.guild_permissions.external_emojis:
            await send_custom_command(custom_command, command_data)


async def send_custom_command(custom_command, command_data):
    message = command_data["message"]
    parser = MetaParser({
        "Author": command_data["message"].author,
        "Arguments": command_data["arguments"].split(' '),
        "Gif": MetaParser.get_gif,
        "Mentions": command_data["message"].mentions,
        "Api": MetaParser.get_api,
        "Random": MetaParser.random_number
    })

    if type(custom_command) is str:
        custom_command = parser.parse_item(custom_command)
        if custom_command != "":
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

        parser.parse_dict(custom_command)
        await message.channel.send(embed=discord.Embed.from_dict(custom_command))
