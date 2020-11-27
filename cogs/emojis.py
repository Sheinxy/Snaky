import discord
from discord.ext import commands
from tools.database import SnakyData
from tools.requests import get_bytes_request


class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add_pack")
    @commands.has_permissions(manage_emojis=True)
    @commands.bot_has_permissions(manage_emojis=True)
    async def _add_pack(self, ctx, user: commands.UserConverter, pack):
        database = SnakyData(f"data/users/{user.id}/emojis/")
        emojis = database.get_data(f"{pack}.json")
        if not emojis:
            await ctx.send(f"{ctx.author.mention}, this pack doesn't exist :c")
            return

        for name, url in emojis.items():
            try:
                await ctx.guild.create_custom_emoji(name=name, image=get_bytes_request(url))
            except Exception as e:
                await ctx.send(f"Skipped emoji {name} because an error occured ({e})", delete_after=3)
        await ctx.send(f"{ctx.author.mention}, added the pack {pack} by {user} to the server!")

    @commands.command(name="del_pack", aliases=["rem_pack"])
    async def _del_pack(self, ctx, name):
        database = SnakyData(f"data/users/{ctx.author.id}/emojis/")
        database.delete_data(f"{name}.json")
        await ctx.send(f"{ctx.author.mention}, deleted the pack {name} ^w^")

    @commands.command(name="list_packs", aliases=["get_packs"])
    async def _list_packs(self, ctx, user: commands.UserConverter):
        database = SnakyData(f"data/users/{user.id}/emojis/")
        packs = ''.join([f"`{pck.replace('.json', '')}`\n" for pck in database.list_dir() if pck.endswith('.json')])
        if not packs:
            packs = "This user doesn't have any pack"
        em = {
            "author": {
                "name": str(ctx.author),
                "icon_url": str(ctx.author.avatar_url_as(static_format='png'))
            },
            "fields": [{
                "name": f"Emoji packs by {user}",
                "inline": True,
                "value": packs
            }]
        }
        await ctx.send(embed=discord.Embed.from_dict(em))

    @commands.command(name="list_emojis", aliases=["get_emojis"])
    async def _list_emojis(self, ctx, user: commands.UserConverter, pack):
        database = SnakyData(f"data/users/{user.id}/emojis/")
        emojis = database.get_data(f"{pack}.json")
        if not emojis:
            await ctx.send(f"{ctx.author.mention}, this pack doesn't exist :c")
            return

        em = {
            "author": {
                "name": str(ctx.author),
                "icon_url": str(ctx.author.avatar_url_as(static_format='png'))
            },
            "fields": [{
                "name": f"Emojis from pack {pack} by {user}",
                "inline": True,
                "value": ' '.join([f"`{emoji}`" for emoji in emojis])
            }]
        }
        await ctx.send(embed=discord.Embed.from_dict(em))

    @commands.command(name="add_emojis", aliases=["add_to_pack"])
    async def _add_emojis(self, ctx, pack: str, *emojis: commands.EmojiConverter):
        add_emojis(ctx.author.id, pack, {emoji.name: emoji.url for emoji in emojis})
        await ctx.send(f"{ctx.author.mention}, I added these emojis to the pack {pack}! ^w^")

    @commands.command(name="del_emojis", aliases=["del_from_pack", "rem_emojis", "rem_from_pack"])
    async def _del_emojis(self, ctx, pack: str, *emojis: commands.EmojiConverter):
        del_emojis(ctx.author.id, pack, [emoji.name for emoji in emojis])
        await ctx.send(f"{ctx.author.mention}, I removed these emojis from the pack {pack}! ^w^")


def add_emojis(user, pack, emojis: dict):
    database = SnakyData(f"data/users/{user}/emojis")
    database.get_data(f"{pack}.json", {})
    for name, url in emojis.items():
        database.set_data(name, str(url), f"{pack}.json")


def del_emojis(user, pack, emojis: list):
    database = SnakyData(f"data/users/{user}/emojis")
    database.get_data(f"{pack}.json", {})
    for name in emojis:
        database.del_data(name, f"{pack}.json")


def setup(bot):
    bot.add_cog(Emojis(bot))
