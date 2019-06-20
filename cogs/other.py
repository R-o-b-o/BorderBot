import discord
from discord.ext import commands
from timeit import default_timer as timer
import math, random, os
from utils import fileHandler
import config

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
    @commands.cooldown(5,600,commands.BucketType.guild)
    async def feedback(self, ctx, *, feedback):
        if feedback is None:
            if random.randint(0, 2) == 0:
                await ctx.send("😡, It's blank you NONCE!")
            else:
                await ctx.send("😕, Is it in invisible ink?")
        else:
            await ctx.send("Thanks, if this is any good I'll give you some garlicoin")
            embed=discord.Embed(description=feedback, color=random.randint(0, 0xFFFFFF))
            embed.set_footer(text=f'From {ctx.author.name}')
            await self.bot.get_channel(560175720052293663).send(embed=embed)

    @commands.command(name='faq', description="See the faq")
    @commands.cooldown(5,600,commands.BucketType.guild)
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

        commands = await fileHandler.GetNumberOfCommands()

        numAvatars = 0
        numUsers = 0
        _, dirs, files = next(os.walk("avatars/"))
        for _, dirs, files in os.walk("avatars/"):
            for _ in dirs:
                numUsers += 1
            for _ in files:
                numAvatars += 1
        
        statsMessage = ("I am in **%d** servers with **%d** users\n"
        "**%d** commands have been made\n"
        "I also have **%d** avatars stored for **%d** users") % (len(guilds), users, commands, numAvatars, numUsers)
        await ctx.send(statsMessage)
    
    @commands.command(name='invite', description="returns an invite link for the bot", aliases=['link'])
    @commands.cooldown(1, 30,commands.BucketType.guild)
    async def invite(self, ctx):
        embed=discord.Embed(title="Bot Invite", description="https://discordapp.com/oauth2/authorize?&client_id=559008680268267528&scope=bot&permissions=536996960", color=0xAD1457)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Other(bot))