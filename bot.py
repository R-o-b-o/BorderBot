import logging
import discord, asyncio, json, aiohttp
from discord.ext import commands, tasks
from datetime import datetime
from utils import fileHandler, borderGen, sql
import config

async def get_prefix(bot, message):
    if isinstance(message.channel, discord.abc.GuildChannel):
        prefix = await sql.get_prefix_from_DB(message.guild.id) or config.prefix
    else:
        prefix = config.prefix
    return commands.when_mentioned_or(prefix)(bot, message)

intents = discord.Intents.default()
intents.members = True

bot = commands.AutoShardedBot(command_prefix=get_prefix,
                   description="A bot to add colorful borders to an avatar! Support Server: https://discord.gg/Dy3anFM",
                   owner_id=config.owner_id,
                   case_insensitive=True,
                   help_command=None,
                   intents=intents,
                   activity=discord.Game(f"{config.prefix}help"),
                   chunk_guilds_at_startup=False)

@bot.event
async def on_ready():
    # update_presence.start()

    bot.loop.create_task(log_guild_stats())
    # bot.loop.create_task(update_botlists())
    
    await sql.add_guilds(guild.id for guild in bot.guilds)
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

    for guild in bot.guilds:
        await guild.chunk(cache=True)

@tasks.loop(minutes=5.0)
async def update_presence():
    await bot.change_presence(activity=discord.Game(f"{config.prefix}help"))

@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, commands.CommandNotFound):
        return
    
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send((f"You have to have `{', '.join(error.missing_perms)}` to use this command."))
    
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention} slow down! Try again in **{error.retry_after:.1f} seconds.**")

    elif isinstance(error, discord.errors.Forbidden):
        await ctx.send("I don't have sufficient permissions for that command.")
    
    elif isinstance(error, discord.errors.HTTPException):
        await ctx.send("The file is too large for me to send, I can only deal with avatars under 8MB.")

    elif isinstance(error, commands.NotOwner):
        await ctx.send("This command can only be made by the **bot owner**")

    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(f"{str(error)}, try sending the full name/nickname, a mention, or their user id")

    else:
        await ctx.send(f"Something went wrong, consider reading the {(await get_prefix(bot, ctx.message))[2]}help {ctx.invoked_with} or join the support server: https://discord.gg/fZJqTAz")

@bot.event
async def on_user_update(before, after):
    if before.avatar != after.avatar and before.avatar is not None:
        borderGen.image_to_static(await fileHandler.download_avatar(before))

        if (after in bot.get_guild(config.support_guild).members) and not(after.bot):
            await send_showcase(after)

@bot.event
async def on_member_join(member):
    if member.guild == bot.get_guild(config.support_guild):
        await member.add_roles(bot.get_guild(config.support_guild).get_role(569663447034494976))

@bot.event
async def on_command_completion(ctx):
    command_logger.info(f"{ctx.command.name} {ctx.author.id}")

@bot.event
async def on_guild_join(guild):
    await sql.add_guild(guild.id)

    embed = discord.Embed(title="Joined server", colour=discord.Colour(0x42f492), description=f"**{guild.name}**", timestamp=datetime.now())
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name="Members", value=len(guild.members))

    await bot.get_channel(574923973704286208).send(embed = embed)

@bot.event
async def on_guild_remove(guild): 
    await sql.remove_guild(guild.id)

    embed = discord.Embed(title="Left server", colour=discord.Colour(0xf43c70), description=f"**{guild.name}**", timestamp=datetime.now())
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name="Members", value=len(guild.members))

    await bot.get_channel(574923973704286208).send(embed=embed)

async def send_showcase(user):
    filepath = await fileHandler.download_avatar(user)

    color = borderGen.get_most_frequent_color(filepath)

    filename = filepath.replace("/", "\\").split("\\")[-1]
    embed=discord.Embed(title=f"{str(user)}", color=int(color.replace('#', ''), 16))
    embed.set_image(url=f"attachment://{filename}")
    
    await bot.get_channel(588808593579573250).send(embed=embed, file=discord.File(filepath, filename=filename))

async def log_guild_stats():
    while not bot.is_closed():
        guilds = bot.guilds
        users = 0
        for guild in guilds:
            users += len(guild.members)

        guild_logger.info("%d %d" % (len(guilds), users))

        await asyncio.sleep(3600)

async def update_botlists():
    guild_count = len(bot.guilds)

    while not bot.is_closed():
        if guild_count != len(bot.guilds):
            guild_count = len(bot.guilds)
            await update_divinebotlist()
            await update_botlistspace()
            
        await asyncio.sleep(600)

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
                botlist_logger.info('divinediscordbots statistics returned {} for {}'.format(resp.status, payload))

async def update_botlistspace():
    if config.blsToken is not None:
        async with aiohttp.ClientSession() as session:
            guild_count = len(bot.guilds)
            payload = json.dumps({
            'server_count': guild_count
            })

            headers = {
                'authorization': config.blsToken,
                'content-type': 'application/json'
            }

            url = 'https://api.botlist.space/v1/bots/{}'.format(bot.user.id)
            async with session.post(url, data=payload, headers=headers) as resp:
                botlist_logger.info('botlistspace statistics returned {} for {}'.format(resp.status, payload))

fileHandler.create_folders()
guild_logger = fileHandler.setup_logger("guilds", "logs/guilds.log")
command_logger = fileHandler.setup_logger("comamnds", "logs/commands.log")
botlist_logger = fileHandler.setup_logger("botlists", "logs/botlists.log") 
for cog in config.cogs:
    bot.load_extension(cog)

sql.create_db()

bot.run(config.token)