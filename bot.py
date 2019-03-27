import discord
from discord.ext import commands
import requests, math, asyncio, random, os
from timeit import default_timer as timer
import border


bot = commands.Bot(command_prefix='>', description="A bot to add colorful borders to an avatar!")

@bot.event
async def on_ready():
    print("ready")
    await bot.change_presence(activity=discord.Game(">help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention} slow down! Try again in {error.retry_after:.1f} seconds.")

@bot.command(name='avatar', description='Gets you a link to someones avatar', aliases=['pfp'], usage="@user")
async def avatar(ctx):
    try:
        member = ctx.message.mentions[0]
    except:
        member = ctx.author
    await ctx.send(member.avatar_url)

@bot.command(name='ping', description='Find how long it takes for the bot to respond')
async def ping(ctx):
    startTime = timer()
    m = await ctx.send(".")
    time = math.trunc((timer() - startTime) * 1000)
    await m.edit(content="that took **%dms**" % time)

@bot.command(name='random', description='Generate a border with random parameters')
@commands.cooldown(5,30)
async def random_command(ctx):
    req = requests.get(ctx.author.avatar_url)
    filepath = "avatars/" + ctx.author.avatar + '.webp'
    open(filepath, 'wb').write(req.content)

    filepath = border.GenerateBasic(filepath, ('#'+"%06x" % random.randint(0, 0xFFFFFF)), random.random() / 2)
    await ctx.send(file=discord.File(filepath))

@bot.command(name='randomTexture', description='Generate a border with random parameters')
@commands.cooldown(5,30)
async def randomTextured_command(ctx):
    req = requests.get(ctx.author.avatar_url)
    filepath = "avatars/" + ctx.author.avatar + '.webp'
    open(filepath, 'wb').write(req.content)

    texturepath = "textures/" + random.choice(os.listdir("textures/"))
    filepath = border.GenerateWithTexture(filepath, texturepath, random.random() / 2)

    await ctx.send(file=discord.File(filepath))

@bot.command(name='border', description='Add a single color border to your avatar', usage="(color) (decimal between 0 - 1)")
@commands.cooldown(2, 5)
async def border_command(ctx):
    if ctx.author.avatar_url.endswith(".gif?size=1024"):
        await ctx.send("Please use the borderGif command instead")
    else:
        startTime = timer()
        
        req = requests.get(ctx.author.avatar_url)

        filepath = "avatars/" + ctx.author.avatar + '.webp'
        open(filepath, 'wb').write(req.content)
        
        downloadTime = math.trunc((timer() - startTime) * 1000)
        startTime = timer()
        
        try:
            colorWidth = ctx.message.content.replace(">border ", "").split()
            
            try:
                size = float(colorWidth[1])
            except:
                size = 0.1

            filepath = border.GenerateBasic(filepath, colorWidth[0], size)
            processTime = math.trunc((timer() - startTime) * 1000)
            startTime = timer()
            
            await ctx.send(file=discord.File(filepath))
            uploadTime = math.trunc((timer() - startTime) * 1000)
            await ctx.send("that took **%dms** to download, **%dms** to process, **%dms** to upload" % (downloadTime, processTime, uploadTime))
        except:
            await ctx.send("Invalid command, please try again")
            await ctx.send("make sure to include a color, the border size is optional")

@bot.command(name='editor', description='This lets you edit your border in real time', aliases=['edit'])
@commands.cooldown(1, 60)
async def editor(ctx):
    req = requests.get(ctx.author.avatar_url)
    filepath = "avatars/" + ctx.author.avatar + '.webp'
    open(filepath, 'wb').write(req.content)
    
    await ctx.send("to change border say: (color = *color*) or (size = *decimal between 0 and 1*) or (texture = *upload texture image*)")
    imageMessage = await ctx.send(file=discord.File(filepath))

    color = "red"
    size = 0.1
    timeMessage = await ctx.send("that took **0ms** to proccess")
    while True:

        def check(m):
            return m.content.replace(" ", "").startswith("size=") or m.content.replace(" ", "").startswith("color=") or m.content.replace(" ", "").startswith("texture=")
            
        try:
            responseMessage = await bot.wait_for('message', timeout=120, check=check)
        except asyncio.TimeoutError:
            await ctx.send("😿 **editor timed out** 😿")
            break

        try:
            startTime = timer()
            if responseMessage.content.replace(" ", "").startswith("size="):
                size = float(responseMessage.content.replace(" ", "").replace("size=", ""))
            elif responseMessage.content.replace(" ", "").startswith("color="):
                color = responseMessage.content.replace(" ", "").replace("color=", "")

            if responseMessage.content.replace(" ", "").startswith("texture="):
                req = requests.get(responseMessage.attachments[0].url)
                texturePath = "textures/" + responseMessage.attachments[0].filename
                open(texturePath, 'wb').write(req.content)
                filepath = border.GenerateWithTexture(filepath, texturePath, size)
            else:
                filepath = border.GenerateBasic(filepath, color, size)

            await imageMessage.delete()
            try:
                await responseMessage.delete()
            except:
                pass
            
            processTime = math.trunc((timer() - startTime) * 1000)
            await timeMessage.edit(content="that took **%dms**" % processTime)

            imageMessage = await ctx.send(file=discord.File(filepath.replace(".webp", ".png")))
        except:
            pass

@bot.command()
async def borderGif(ctx):
    await ctx.send("baited 🎣")

bot.run("NTU5MDA4NjgwMjY4MjY3NTI4.D3foPw.OTDU0IHH9hSGji3RV7Kq2q8ml34")