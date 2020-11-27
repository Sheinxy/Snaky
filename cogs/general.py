import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def _help(self, ctx):
        em = {
            "title": "Hellow! I'm Snaky, your friendly neighborhood Snake Robot!",
            "description": "Prefix: -\n",
            "url": "https://sheinxy.github.io/projects/Snaky",
            "thumbnail": {
                "url": str(self.bot.user.avatar_url_as(static_format='png'))
            },
            "author": {
                "name": str(ctx.author),
                "icon_url": str(ctx.author.avatar_url_as(static_format='png'))
            },
            "footer": {
                "text": "Bot created by https://sheinxy.github.io",
                "icon_url": "https://www.gravatar.com/avatar/88a7ac03b956d2e189af6b3fa6dc6ebe?s=150"
            },
            "color": 9276813,
            "fields": [
            ]
        }
        for cog_name, cog in self.bot.cogs.items():
            em["fields"].append({
                "name": cog_name,
                "value": '\n'.join([f"`{command.name}`" for command in cog.get_commands()]),
                "inline": True
            })
        await ctx.send(embed=discord.Embed.from_dict(em))

    @commands.command(name="ping")
    async def _ping(self, ctx):
        await ctx.send("Pong")

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def _clear(self, ctx, x: int):
        if x < 1:
            return
        deleted, x = -1, x + 1
        while x > 0:
            deleted += len(await ctx.channel.purge(limit=x))
            x -= 100
        await ctx.send(
            f"{ctx.author.mention} I have cleared {deleted} message(s) (proud of me? :3c)",
            delete_after=3
        )


def setup(bot):
    bot.add_cog(General(bot))
