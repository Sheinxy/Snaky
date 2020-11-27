import discord
from discord.ext import commands


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load")
    @commands.is_owner()
    async def _load(self, ctx, *args):
        for arg in args:
            self.bot.load_extension(arg)
        await ctx.send(f"{ctx.author.mention}: Loaded {list(args)} ! :3c", delete_after=3)

    @commands.command(name="reload")
    @commands.is_owner()
    async def _reload(self, ctx, *args):
        for arg in args:
            self.bot.reload_extension(arg)
        await ctx.send(f"{ctx.author.mention}: Reloaded {list(args)} ! :3c", delete_after=3)

    @commands.command(name="reload_all")
    @commands.is_owner()
    async def _reload_all(self, ctx):
        exts = list(self.bot.extensions.keys())
        for ext in exts:
            self.bot.reload_extension(ext)
        await ctx.send(f"{ctx.author.mention}: Reloaded all extensions!", delete_after=3)


def setup(bot):
    bot.add_cog(Dev(bot))
