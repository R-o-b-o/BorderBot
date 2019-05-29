import discord
from discord.ext import commands
from timeit import default_timer as timer
import math, random, os, asyncio
import fileHandler, borderGen, config

async def hasManageGuild(ctx):
    return ctx.author.guild_permissions.manage_guild

class Guild(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="guildBorder")
    @commands.check(hasManageGuild)
    async def guildBorder(self, ctx, color="default", size : float=0.1):
        filepath = await fileHandler.downloadGuildIcon(ctx.guild)
        
        if color == "default":
            color = borderGen.GetMostFrequentColor(filepath)
        
        try:
            fileBytes = borderGen.GenerateBasic(filepath, color, size)
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
    @commands.check(hasManageGuild)
    async def guildIconReset(self, ctx):
        await ctx.guild.edit(icon = await fileHandler.getFileBytesFromFile(f"guilds/{ctx.guild.id}.{config.imageFormat}"))
        await ctx.message.add_reaction("☑")
        

def setup(bot):
    bot.add_cog(Guild(bot))