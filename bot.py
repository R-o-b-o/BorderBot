import logging
import discord, asyncio
from discord.ext import commands
from datetime import datetime
from utils import fileHandler
import config

bot = commands.Bot(command_prefix=config.prefix, description="A bot to add colorful borders to an avatar! Support Server: https://discord.gg/Dy3anFM", owner_id=config.owner_id, case_insensitive=True)

@bot.event
async def on_ready():
    #bot.remove_command('help')
    await bot.change_presence(activity=discord.Game(f"{config.prefix}help"))
    bot.loop.create_task(log_guild_stats())
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.CheckFailure):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You have to have the `manage guild` permission to use this command")
    
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention} slow down! Try again in {error.retry_after:.1f} seconds.")

    elif isinstance(error, discord.errors.Forbidden):
        await ctx.send("I don't have sufficient permissions for that command.")
    
    else:
        await ctx.send(f"Something went wrong, consider reading the **{bot.command_prefix}help {ctx.invoked_with}**")

@bot.event
async def on_user_update(before, after):
    if before.avatar != after.avatar:
        await fileHandler.downloadAvatar(before)

@bot.event
async def on_command_completion(ctx):
    commandLogger.info(ctx.command.name)

@bot.event
async def on_guild_join(ctx):
    await bot.get_user(344270500987404288).send("BorderBot has joined a new server! ㊗")

async def log_guild_stats():
    while True:
        guilds = bot.guilds
        users = 0
        for guild in guilds:
            users += len(guild.members)

        guildLogger.info("%d %d" % (len(guilds), users))

        await asyncio.sleep(3600)

fileHandler.CreateFolders()
guildLogger = fileHandler.setupLogger("guilds", "logs/guilds.log")
commandLogger = fileHandler.setupLogger("comamnds", "logs/commands.log")
for cog in config.cogs:
    bot.load_extension(cog) 

bot.run(config.token)