import discord
import json
from discord.ext import commands
from cogs.macros import launch_macro, load_macros

bot = commands.Bot(command_prefix='-', help_command=None, owner_id=234437740958056448)


@bot.event
async def on_ready():
    activity = discord.Game("I'm a robot snake ^w^")
    await bot.change_presence(activity=activity, status=discord.Status.idle)
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot or not message.content.startswith(bot.command_prefix):
        return

    command, args = message.content.split(' ')[0].replace(bot.command_prefix, ''), message.content.split(' ')[1:]
    user_folder = f"users/{message.author.id}"
    guild_folder = None if not message.guild else f"guilds/{message.guild.id}"

    if await bot.process_commands(message):
        await message.channel.trigger_typing()
    elif command in (macros := load_macros(user_folder, guild_folder)):
        if not message.guild or "nsfw" not in macros[command] or message.channel.nsfw:
            await message.channel.trigger_typing()
            await launch_macro(message, args, macros[command])
        else:
            await message.channel.send(f"{message.author.mention} This is not sfw, naughty! >:3", delete_after=3)


@bot.event
async def on_command_error(ctx, error):
    err = getattr(error, "original", error)

    if isinstance(err, commands.CommandNotFound):
        return
    else:
        print(err)


def setup(*extensions):
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(json.load(open("config.json", 'r'))["TOKEN"])
