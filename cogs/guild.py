import discord
from discord.ext import commands
import asyncio, os
from utils import fileHandler, borderGen, sql
import config

class Guild(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.UpdateGuilds())

    @commands.command(name="guildBorder")
    @commands.cooldown(2,10,commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    async def guildBorder(self, ctx, color="default", size : float=0.1):
        filepath = await fileHandler.downloadGuildIcon(ctx.guild)
        
        if color == "default":
            color = borderGen.GetMostFrequentColor(filepath)
        
        try:
            fileBytes = await borderGen.GenerateBasic(filepath, color, size, imageFormat="png")
        except ValueError:
            await ctx.send("I could not find color: **%s**\nFor the list of possible color names: https://www.w3schools.com/colors/colors_names.asp" % color)
            return
        
        await ctx.send(file=discord.File(fileBytes, filename=color + "-" + str(size) + ".png"))

        reactionMessage = await ctx.send("Would you like to use this as the guild icon?")
        await reactionMessage.add_reaction("❌")
        await reactionMessage.add_reaction("☑")

        def check(reaction, user):
            return user == ctx.author

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60, check=check)

            if str(reaction.emoji) == '☑':
                fileBytes.seek(0)
                await ctx.guild.edit(icon = fileBytes.read())
                await reactionMessage.edit(content="The icon has been changed")
            else:
                await reactionMessage.edit(content="The icon has not been changed")
        except asyncio.TimeoutError:
            pass
        
        await reactionMessage.clear_reactions()
    
    @commands.command(name="guildIconReset")
    @commands.has_permissions(manage_guild=True)
    async def guildIconReset(self, ctx):
        await ctx.guild.edit(icon = await fileHandler.getFileBytesFromFile(f"guilds/{ctx.guild.id}.png"))
        await ctx.message.add_reaction("☑")
    
    @commands.command(name="endSlideshow")
    @commands.has_permissions(manage_guild=True)
    async def endSlideShow(self, ctx):
        await sql.RemoveIconChanger(ctx.guild.id)
        await fileHandler.clearFolder(ctx.guild.id)
        await ctx.send("`The slideshow feature has been disabled for this guild`")

    @commands.command(name="slideshow", description='Sets up a rotating guild icon', usage='(number of images) (interval time in hours)')
    @commands.has_permissions(manage_guild=True)
    async def slideShow(self, ctx, numImages : int, interval : int=24):
        if numImages < 2 or interval < 1:
            await ctx.send("The interval time and number of images must be above 0")
            return

        await ctx.send(f"Now send the {numImages} image(s)")
        def check(m):
            return m.author == ctx.author and len(m.attachments) != 0

        attachments = []
        for _ in range(numImages):    
            try:
                responseMessage = await self.bot.wait_for('message', timeout=120, check=check)
            except asyncio.TimeoutError:
                await ctx.send("`You took too long, you must retry the command`")
            attachments.append(responseMessage.attachments[0].url)

        await fileHandler.setupSlideshow(ctx.guild.id, attachments)
        await sql.AddIconChanger(ctx.guild.id, interval)

        await ctx.send("The slideshow has been set up, use `endSlideshow` to end it")

    async def UpdateGuild(self, guildId, imageBytes):   
        await self.bot.get_guild(guildId).edit(icon = imageBytes)

    async def UpdateGuilds(self):
        await self.bot.wait_until_ready()
        
        count = 0
        while not self.bot.is_closed():
            iconChanges = [x for x in await sql.GetIconChanages() if count % x[1] == 0]
            if len(iconChanges) != 0:
                for iconChange in iconChanges:
                    filepaths = fileHandler.getFilepaths("guilds/" + str(iconChange[0]) + "/")
                    
                    await self.bot.loop.create_task(self.UpdateGuild(iconChange[0], await fileHandler.getFileBytesFromFile(filepaths[iconChange[2] % len(filepaths)])))

                await sql.IncrementIconChanger([x[0] for x in iconChanges])

                count += 1
            await asyncio.sleep(3600)
        

def setup(bot):
    bot.add_cog(Guild(bot))