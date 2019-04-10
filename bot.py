import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import fileHandler

bot = commands.Bot(command_prefix='>', description="A bot to add colorful borders to an avatar! Test Server: https://discord.gg/Dy3anFM")
cogs = ['cogs.avatar', 'cogs.border', 'cogs.other']

@bot.event
async def on_ready():
    #bot.remove_command('help')
    await bot.change_presence(activity=discord.Game(">help"))
    for cog in cogs:
        bot.load_extension(cog)
    
    await fileHandler.CreateFolders()
    await fileHandler.SetupLogging("logs/commands.log")
    await fileHandler.SetupLogging("logs/guilds.log")
    bot.loop.create_task(log())
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention} slow down! Try again in {error.retry_after:.1f} seconds.")

@bot.event
async def on_member_update(before, after):
    if before.avatar != after.avatar:
        await fileHandler.downloadAvatar(before)

@bot.event
async def on_command_completion(ctx):
    f = open("logs/commands.log", "a")
    f.write("\n%s %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ctx.command.name))

async def log():
    while True:
        guilds = bot.guilds
        users = 0
        for guild in guilds:
            users += len(guild.members)

        f = open("logs/guilds.log", "a")
        f.write("\n%s %d %d" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), len(guilds), users))

        with open('logs/guilds.log') as f:
            lastLine = f.readlines()
        lastLine = lastLine[-2]
        oldGuilds = lastLine.split()[2]
        
        if len(guilds) > int(oldGuilds):
            await bot.get_user(344270500987404288).send("BorderBot has joined %d new server(s)! ㊗" % (len(guilds) - int(oldGuilds)))

        await asyncio.sleep(600)

bot.run("NTU5MDA4NjgwMjY4MjY3NTI4.D3foPw.OTDU0IHH9hSGji3RV7Kq2q8ml34")