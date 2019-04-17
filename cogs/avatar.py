import discord
from discord.ext import commands
import os, random

class Avatar(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='avatar', description='Gets you a link to someones avatar', aliases=['pfp'], usage="@user")
    async def avatar(self, ctx):
        try:
            member = ctx.message.mentions[0]
        except:
            member = ctx.author
        await ctx.send(member.avatar_url)
    
    @commands.command(name='history', description='See a history of your avatar', aliases=['avatars'])
    @commands.cooldown(1,300)
    async def history(self, ctx):
        files = []
        filepath = "avatars/" + str(ctx.author.id) + "/"
        for file in os.listdir(filepath):
            files.append(discord.File(filepath + file))
        
        for i in range(0, len(files), 10):
            await ctx.author.send(files=files[i:i+10])
    
    @commands.command(name='randomAvatar', description='Receive a random avatar')
    @commands.cooldown(5,30)
    async def randomAvatar(self, ctx):
        filepaths = []
        for path, _, files in os.walk("avatars/"):
            for name in files:
                filepaths.append(os.path.join(path, name))
        await ctx.send(file=discord.File(random.choice(filepaths)))

def setup(bot):
    bot.add_cog(Avatar(bot))