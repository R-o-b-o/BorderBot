import discord
from discord.ext import commands
import inspect
import config

class Owner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='eval', hidden=True)
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        to_eval = code.replace("await ", "")
        try:
            result = eval(to_eval)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            result = type(e).__name__ + ": " + str(e)

        await ctx.send(f"```Python\n{result}```")


    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, cog = "all"):
        if cog == "all":
            failed = 0
            success = 0
            for cog in config.cogs:
                try:
                    self.bot.reload_extension(cog)
                    success += 1
                except:
                    failed += 1

            await ctx.send(f"Reloaded all cogs.\n**Success**: {success} **Failed**: {failed}")
            return
        else:
            try:
                self.bot.reload_extension("cogs." + cog)
                await ctx.send(f"Successfully reloaded the cog **{cog}**.")
            except:
                await ctx.send(f"Error reloading the cog **{cog}**.")
    
    @commands.is_owner()
    @commands.command(name='sudo', hidden=True)
    async def sudo(self, ctx, member: discord.Member, *, msg):
        webhook = await ctx.channel.create_webhook(name="sudo")
        await webhook.send(content=msg, username=member.name, avatar_url=member.avatar_url)
        await webhook.delete()

        message = ctx.message
        message.author = member
        message.content = msg
        ctx = await self.bot.get_context(message)
        await self.bot.invoke(ctx)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Owner(bot))