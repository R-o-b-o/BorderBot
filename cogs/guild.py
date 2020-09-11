import discord
from discord.ext import commands
import asyncio, os
from utils import fileHandler, borderGen, sql
import config

class Guild(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.UpdateGuilds())

    @commands.command(name="guildBorder", hidden=True)
    @commands.cooldown(2,10,commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    async def guildBorder(self, ctx, color="default", size : float=0.1):
        filepath = await fileHandler.download_guild_icon(ctx.guild)
        
        if color == "default":
            color = borderGen.get_most_frequent_color(filepath)
        
        try:
            file_bytes = await borderGen.generate_basic(filepath, color, size, image_format="png")
        except ValueError:
            await ctx.send("I could not find color: **%s**\nFor the list of possible color names: https://www.w3schools.com/colors/colors_names.asp" % color)
            return
        
        await ctx.send(file=discord.File(file_bytes, filename=color + "-" + str(size) + ".png"))

        reaction_msg = await ctx.send("Would you like to use this as the guild icon?")
        await reaction_msg.add_reaction("❌")
        await reaction_msg.add_reaction("☑")

        def check(reaction, user):
            return user == ctx.author

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60, check=check)

            if str(reaction.emoji) == '☑':
                file_bytes.seek(0)
                await ctx.guild.edit(icon = file_bytes.read())
                await reaction_msg.edit(content="The icon has been changed")
            else:
                await reaction_msg.edit(content="The icon has not been changed")
        except asyncio.TimeoutError:
            pass
        
        await reaction_msg.clear_reactions()
    
    @commands.command(name="guildIconReset", hidden=True)
    @commands.has_permissions(manage_guild=True)
    async def guildIconReset(self, ctx):
        await ctx.guild.edit(icon = await fileHandler.get_bytes_from_file(f"guilds/{ctx.guild.id}.png"))
        await ctx.message.add_reaction("☑")
    
    @commands.command(name="endSlideshow", description="End guild icon slideshow")
    @commands.has_permissions(manage_guild=True)
    async def endSlideShow(self, ctx):
        await sql.remove_icon_changer(ctx.guild.id)
        fileHandler.clear_guild_folder(ctx.guild.id)
        await ctx.send("`The slideshow feature has been disabled for this guild`")

    @commands.command(name="slideshow", description='Set up a rotating guild icon', usage='(# of images) (interval time in hours)')
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
                response_msg = await self.bot.wait_for('message', timeout=120, check=check)
                attachments.append(response_msg.attachments[0].url)
            except asyncio.TimeoutError:
                await ctx.send("`You took too long, you must retry the command`")
                return
        
        await ctx.channel.trigger_typing()
        await fileHandler.setup_slideshow(ctx.guild.id, attachments)
        await sql.add_icon_changer(ctx.guild.id, interval)

        await ctx.send("The slideshow has been set up, use `endSlideshow` to end it")

    async def UpdateGuild(self, guildId, imageBytes): 
        try:  
            await self.bot.get_guild(guildId).edit(icon = imageBytes)
        except:
            pass

    async def UpdateGuilds(self):
        await self.bot.wait_until_ready()
        
        count = 0
        while not self.bot.is_closed():
            icon_changes = [x for x in await sql.get_icon_changes() if count % x[1] == 0]
            if len(icon_changes) != 0:
                for iconChange in icon_changes:
                    filepaths = fileHandler.get_filepaths("guilds/" + str(iconChange[0]) + "/")
                    
                    await self.bot.loop.create_task(self.UpdateGuild(iconChange[0], await fileHandler.get_bytes_from_file(filepaths[iconChange[2] % len(filepaths)])))

                await sql.increment_icon_changer([x[0] for x in icon_changes])

                count += 1
            await asyncio.sleep(3600)
        

def setup(bot):
    bot.add_cog(Guild(bot))