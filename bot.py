import logging
import discord, asyncio, json, aiohttp
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
    await update_divinebotlist()
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, commands.CommandNotFound):
        return
    
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send((f"You have to have `{', '.join(error.missing_perms)}` to use this command."))
    
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention} slow down! Try again in {error.retry_after:.1f} seconds.")

    elif isinstance(error, discord.errors.Forbidden):
        await ctx.send("I don't have sufficient permissions for that command.")
    
    elif isinstance(error, discord.errors.HTTPException):
        await ctx.send("The file is too large for me to send, I can only deal with avatars under 8MB.")

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
async def on_guild_join(guild):
    embed = discord.Embed(title="Joined server", colour=discord.Colour(0x42f492), description=f"**{guild.name}**", timestamp=datetime.now())
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name="Members", value=len(guild.members))

    await update_divinebotlist()
    await bot.get_channel(574923973704286208).send(embed = embed)

@bot.event
async def on_guild_remove(guild): 
    embed = discord.Embed(title="Left server", colour=discord.Colour(0xf43c70), description=f"**{guild.name}**", timestamp=datetime.now())
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name="Members", value=len(guild.members))

    await update_divinebotlist()
    await bot.get_channel(574923973704286208).send(embed = embed)

async def log_guild_stats():
    while True:
        guilds = bot.guilds
        users = 0
        for guild in guilds:
            users += len(guild.members)

        guildLogger.info("%d %d" % (len(guilds), users))

        await asyncio.sleep(3600)

async def update_divinebotlist():
    if config.ddblToken is not None:
        async with aiohttp.ClientSession() as session:
            guild_count = len(bot.guilds)
            payload = json.dumps({
            'server_count': guild_count
            })

            headers = {
                'authorization': config.ddblToken,
                'content-type': 'application/json'
            }

            url = 'https://divinediscordbots.com/bot/{}/stats'.format(bot.user.id)
            async with session.post(url, data=payload, headers=headers) as resp:
                print('divinediscordbots statistics returned {} for {}'.format(resp.status, payload))

fileHandler.CreateFolders()
guildLogger = fileHandler.setupLogger("guilds", "logs/guilds.log")
commandLogger = fileHandler.setupLogger("comamnds", "logs/commands.log")
for cog in config.cogs:
    bot.load_extension(cog) 

bot.run(config.token)