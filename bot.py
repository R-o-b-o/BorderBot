import discord
from discord.ext import commands
import asyncio
from datetime import datetime

bot = commands.Bot(command_prefix='>', description="A bot to add colorful borders to an avatar!")
cogs = ['cogs.border', 'cogs.other']

@bot.event
async def on_ready():
    #bot.remove_command('help')
    for cog in cogs:
        bot.load_extension(cog)
    await bot.change_presence(activity=discord.Game(">help"))
    bot.loop.create_task(log())
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention} slow down! Try again in {error.retry_after:.1f} seconds.")

async def log():
    while True:
        guilds = len(list(bot.guilds))
        f = open("logs/guilds.log", "a")
        f.write("%s %d\n" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), guilds))
        await asyncio.sleep(600)

bot.run("NTU5MDA4NjgwMjY4MjY3NTI4.D3foPw.OTDU0IHH9hSGji3RV7Kq2q8ml34")