import discord
from discord.ext import commands
import os, random, math
from timeit import default_timer as timer
import fileHandler, borderGen

class Avatar(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='avatar', description='Gets you a link to someones avatar', aliases=['pfp'], usage="@user")
    async def avatar(self, ctx):
        if len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]
        else:
            member = ctx.author

        url = member.avatar_url_as(format='png', size=1024)
        if str(member.avatar_url).endswith(".gif?size=1024"):
            url = member.avatar_url
        
        if random.randint(0, 5) == 0:
            embed=discord.Embed(description=f"[Avatar Link]({url})", color=0xAD1457)
            embed.set_thumbnail(url=url)
            embed.set_image(url=url)
            embed.set_author(name=f"{member.name}", icon_url=url)
            embed.set_footer(text=".", icon_url=url)

            webhook = await ctx.channel.create_webhook(name="BorderBot")
            await webhook.send(embed=embed, avatar_url=url)
            await webhook.delete()
        else:
            embed=discord.Embed(title=f"{member.name}", description=f"[Avatar Link]({url})", color=0xAD1457)
            embed.set_thumbnail(url=url)
            embed.set_image(url=url)
        
            await ctx.send(embed=embed)
    
    @commands.command(name='history', description='See a history of your avatar', aliases=['avatars'])
    @commands.cooldown(2,300)
    async def history(self, ctx):
        startTime = timer()
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            await ctx.send("Dmed previous avatars 🖼!")
        files = []
        filepaths = []
        filepath = "avatars/" + str(ctx.author.id) + "/"
        for file in os.listdir(filepath):
            filepaths.append(filepath + file)
            files.append(discord.File(filepath + file))
        fileBytes = borderGen.GetavatarHistoryImage(filepaths)
        await ctx.send("that took **"+str(math.trunc((timer() - startTime) * 1000))+"** ms", file=discord.File(fileBytes, filename="history.png"))
        for i in range(0, len(files), 10):
            await ctx.author.send(files=files[i:i+10])
    
    @commands.command(name='randomAvatar', description='Receive a random avatar')
    @commands.cooldown(10,30)
    async def randomAvatar(self, ctx):
        filepaths = []
        for path, _, files in os.walk("avatars/"):
            for name in files:
                filepaths.append(os.path.join(path, name))
        await ctx.send(file=discord.File(random.choice(filepaths)))

    @commands.command(name='avatarColors', description='Gets you n dominant colors', aliases=['avatarcolours, colors'], usage="(number of colors)")
    @commands.cooldown(10,30)
    async def avatarColors(self, ctx, numColors = 5):
        filepath = await fileHandler.downloadAvatar(ctx.author)
        fileBytes = borderGen.GetDominantColors(filepath, numColors)
        await ctx.send(file=discord.File(fileBytes, filename="colors.png"))


def setup(bot):
    bot.add_cog(Avatar(bot))