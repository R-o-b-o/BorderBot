import discord
from discord.ext import commands
from timeit import default_timer as timer
import math, random
import fileHandler

class Other(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ping', description='Find out how long it takes for the bot to respond')
    async def ping(self, ctx):
        startTime = timer()
        m = await ctx.send(".")
        time = math.trunc((timer() - startTime) * 1000)
        await m.edit(content="that took **%dms**" % time)

    @commands.command(name='feedback', description="Give feedback to improve the bot's functionality", aliases=['question'], usage="Feedback-Goes-Here")
    @commands.cooldown(5,600)
    async def feedback(self, ctx):
        if ctx.message.content.replace(">feedback", "") == "" or ctx.message.content.replace(">question", "") == "":
            if random.randint(0, 2) == 0:
                await ctx.send("😡, It's blank you NONCE!")
            else:
                await ctx.send("😕, Is it in invisible ink?")
        else:
            await fileHandler.addFeedback(ctx.message.content.replace(">feedback", "").replace(">question", ""))
            await ctx.send("Thanks, if this is any good I'll give you some garlicoin")

    @commands.command(name='faq', description="See the faq")
    @commands.cooldown(5,600)
    async def faq(self, ctx):
        f = open("FAQ.md", "r")
        embed=discord.Embed(title="FAQ", description=f.read(), color=0xAD1457)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='stats')
    async def stats(self, ctx):
        guilds = self.bot.guilds
        users = 0
        for guild in guilds:
            users += len(guild.members)

        await ctx.send("we are in **%d** servers with **%d** users" % (len(guilds), users))
    
    @commands.command(name='invite', description="returns an invite link for the bot", aliases=['link'])
    @commands.cooldown(1, 30)
    async def invite(self, ctx):
        await ctx.send("https://discordapp.com/oauth2/authorize?&client_id=559008680268267528&scope=bot&permissions=536995904")

def setup(bot):
    bot.add_cog(Other(bot))