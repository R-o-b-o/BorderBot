import discord
from discord.ext import commands
import os, random

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
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            await ctx.send("Dmed previous avatars 🖼!")
        files = []
        filepath = "avatars/" + str(ctx.author.id) + "/"
        for file in os.listdir(filepath):
            files.append(discord.File(filepath + file))
        
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

def setup(bot):
    bot.add_cog(Avatar(bot))