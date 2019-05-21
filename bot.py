import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import fileHandler, config

bot = commands.Bot(command_prefix=config.prefix, description="A bot to add colorful borders to an avatar! Support Server: https://discord.gg/Dy3anFM", owner_id=config.owner_id, case_insensitive=True)

@bot.event
async def on_ready():
    #bot.remove_command('help')
    await bot.change_presence(activity=discord.Game(f"{config.prefix}help"))
    try:
        for cog in config.cogs:
            bot.load_extension(cog)
        
        fileHandler.CreateFolders()
        bot.loop.create_task(log())
    except commands.errors.ExtensionAlreadyLoaded:
        print("Tried to reload extension")
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, commands.CommandNotFound):
        return
    
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention} slow down! Try again in {error.retry_after:.1f} seconds.")

    elif isinstance(error, discord.errors.Forbidden):
        await ctx.send("I don't have sufficient permissions for that command.")
    
    else:
        await ctx.send(f"Invalid parameters, consider reading the **{bot.command_prefix}help {ctx.invoked_with}**")

@bot.event
async def on_user_update(before, after):
    if before.avatar != after.avatar:
        await fileHandler.downloadAvatar(before)

@bot.event
async def on_command_completion(ctx):
    f = open("logs/commands.log", "a+")
    f.write("\n%s %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ctx.command.name))

@bot.event
async def on_guild_join(ctx):
    await bot.get_user(344270500987404288).send("BorderBot has joined a new server! ㊗")

async def log():
    while True:
        guilds = bot.guilds
        users = 0
        for guild in guilds:
            users += len(guild.members)

        f = open("logs/guilds.log", "a+")
        f.write("\n%s %d %d" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), len(guilds), users))

        await asyncio.sleep(600)

bot.run(config.token)