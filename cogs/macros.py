import discord
import json
from discord.ext import commands
from tools.database import SnakyData
from tools.parse_macros import parse_macro


class Macros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="def_macro", aliases=["add_macro"])
    async def _macro(self, ctx, name, *, macro: json.loads):
        if ctx.guild:
            set_macro(f"guilds/{ctx.guild.id}", name, macro)
        else:
            set_macro(f"users/{ctx.author.id}", name, macro)
        await ctx.send(f"{ctx.author.mention}: I created the macro {name}! :3c")

    @commands.command(name="undef_macro", aliases=["rem_macro", "del_macro"])
    async def _del_macro(self, ctx, name):
        if ctx.guild:
            del_macro(f"guilds/{ctx.guild.id}", name)
        else:
            del_macro(f"users/{ctx.author.id}", name)
        await ctx.send(f"{ctx.author.mention}: I removed the macro {name}! :3c")

    @commands.command(name="list_macros", aliases=["macros", "all_macros"])
    async def _list_macros(self, ctx):
        database = SnakyData("data")
        base_macros = database.get_data("macros.json")
        user_macros = database.get_data(f"users/{ctx.author.id}/macros.json", base_macros)
        guild_macros = {} if not ctx.guild else database.get_data(f"guilds/{ctx.guild.id}/macros.json", base_macros)
        em = {
            "author": {
                "name": str(ctx.author),
                "icon_url": str(ctx.author.avatar_url_as(static_format='png'))
            },
            "color": 9276813,
            "fields": [
                {
                    "name": "Your macros are:",
                    "value": ' '.join([f"`{macro}`" for macro in user_macros]),
                    "inline": False
                }
            ]
        }
        if guild_macros:
            em["fields"].append({
                "name": "This guild's macros are:",
                "value": ' '.join([f"`{macro}`" for macro in guild_macros]),
                "inline": False
            })
        await ctx.send(embed=discord.Embed.from_dict(em))

    @commands.command(name="show_macro", aliases=["analyse_macro", "code_macro"])
    async def _show_macros(self, ctx, name):
        macros = load_macros(f"users/{ctx.author.id}", None if not ctx.guild else f"guilds/{ctx.guild.id}")
        if name in macros:
            em = {
                "author": {
                    "name": str(ctx.author),
                    "icon_url": str(ctx.author.avatar_url_as(static_format='png'))
                },
                "color": 9276813,
                "fields": [
                    {
                        "name": name,
                        "value": f"```json\n{json.dumps(macros[name], indent=2)}```",
                        "inline": False
                    }
                ]
            }
            await ctx.send(embed=discord.Embed.from_dict(em))
        else:
            await ctx.send(f"{ctx.author.mention}, I am sorry but this macro cannot be found :,(")

    @commands.command(name="execute", aliases=["launch", "do"])
    async def _execute(self, ctx, *, macro: json.loads):
        await launch_macro(ctx.message, [], macro)


def del_macro(folder: str, name: str):
    database = SnakyData("data")
    load_macros(folder, "")
    database.get_ref(folder).del_data(name, "macros.json")


def set_macro(folder: str, name: str, macro: dict):
    database = SnakyData("data")
    load_macros(folder, "")
    database.get_ref(folder).set_data(name, macro, "macros.json")


def load_macros(user_folder: str, guild_folder: str):
    database = SnakyData("data")
    base_macros = database.get_data("macros.json")
    user_macros = database.get_data(f"{user_folder}/macros.json", base_macros)
    guild_macros = {} if not guild_folder else database.get_data(f"{guild_folder}/macros.json", base_macros)
    return {**user_macros, **guild_macros}


async def launch_macro(message: discord.Message, args: list, macro: dict):
    macro = parse_macro(macro, {"message": message, "author": message.author, "guild": message.guild, "args": args})
    content = None if "content" not in macro else macro["content"]
    em = None if "embed" not in macro else discord.Embed.from_dict(macro["embed"])
    if content is not None or em is not None:
        await message.channel.send(content, embed=em)


def setup(bot):
    bot.add_cog(Macros(bot))
