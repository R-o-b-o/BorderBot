import discord
from discord.ext import commands
import requests, math, asyncio, random, os
from timeit import default_timer as timer
import borderGen

class Border(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='avatar', description='Gets you a link to someones avatar', aliases=['pfp'], usage="@user")
    async def avatar(self, ctx):
        try:
            member = ctx.message.mentions[0]
        except:
            member = ctx.author
        await ctx.send(member.avatar_url)

    @commands.command(name='random', description='Generate a border with random parameters', usage="number of images to generate (max 5)")
    @commands.cooldown(5,30)
    async def random_command(self, ctx, times : int=1):
        if  (times <= 5):
            for _ in range(0,times):
                req = requests.get(ctx.author.avatar_url)

                if ctx.author.avatar_url.endswith(".gif?size=1024"):
                    filepath = "avatars/" + ctx.author.avatar + '.gif'
                    open(filepath, 'wb').write(req.content)
                    filepath = borderGen.GenerateBasic(filepath, ("#%06x" % random.randint(0, 0xFFFFFF)), random.random() / 5 + 0.05)
                else:
                    filepath = "avatars/" + ctx.author.avatar + '.webp'
                    open(filepath, 'wb').write(req.content)
                    borderGen.GenerateGif(filepath, ("#%06x" % random.randint(0, 0xFFFFFF)), random.random() / 5 + 0.05)
                
                await ctx.send(file=discord.File(filepath))
        else:
            await ctx.send("There is a maximun of 5, *sorry*")

    @commands.command(name='randomTexture', description='Generate a border with a random texture')
    @commands.cooldown(5,30)
    async def randomTexture_command(self, ctx):
        req = requests.get(ctx.author.avatar_url)
        texturepath = "textures/" + random.choice(os.listdir("textures/"))

        if ctx.author.avatar_url.endswith(".gif?size=1024"):
            filepath = "avatars/" + ctx.author.avatar + '.gif'
            open(filepath, 'wb').write(req.content)
            borderGen.GenerateGifWithTexture(filepath, texturepath, random.random() / 5 + 0.05)
        else:
            filepath = "avatars/" + ctx.author.avatar + '.webp'
            open(filepath, 'wb').write(req.content)
            filepath = borderGen.GenerateWithTexture(filepath, texturepath, random.random() / 5 + 0.05)

        await ctx.send(file=discord.File(filepath))

    @commands.command(name='border', description='Add a single color border to your avatar', usage="(color) (decimal between 0 - 1) [defaults to size 0.1 and the most occuring color]")
    @commands.cooldown(2, 5)
    async def border_command(self, ctx, color="default", size : float=0.1):
        try:
            startTime = timer()

            req = requests.get(ctx.author.avatar_url)

            if ctx.author.avatar_url.endswith(".gif?size=1024"):
                filepath = "avatars/" + ctx.author.avatar + '.gif'
            else:
                filepath = "avatars/" + ctx.author.avatar + '.webp'

            open(filepath, 'wb').write(req.content)
                
            downloadTime = math.trunc((timer() - startTime) * 1000)
            startTime = timer()
                    
            if color == "default":
                color = borderGen.GetMostFrequentColor(filepath)
            
            if ctx.author.avatar_url.endswith(".gif?size=1024"):
                borderGen.GenerateGif(filepath, color, size)
            else:
                filepath = borderGen.GenerateBasic(filepath, color, size)
            
            processTime = math.trunc((timer() - startTime) * 1000)
            startTime = timer()
                    
            await ctx.send(file=discord.File(filepath))
            uploadTime = math.trunc((timer() - startTime) * 1000)
            await ctx.send("that took **%dms** to download, **%dms** to process, **%dms** to upload" % (downloadTime, processTime, uploadTime))
        except:
            await ctx.send("Invalid command, consider reading the **>help border**")

    @commands.command(name='editor', description='Lets you edit your border in real time!', aliases=['edit'])
    @commands.cooldown(1, 60)
    async def editor(self, ctx):
        req = requests.get(ctx.author.avatar_url)
        if ctx.author.avatar_url.endswith(".gif?size=1024"):
            filepath = "avatars/" + ctx.author.avatar + '.gif'
        else:
            filepath = "avatars/" + ctx.author.avatar + '.webp'
        open(filepath, 'wb').write(req.content)
        
        await ctx.send("to change border say: (color = *color*) or (size = *decimal between 0 and 1*) or (texture = *upload texture image*)")
        imageMessage = await ctx.send(file=discord.File(filepath))

        color = "red"
        size = 0.1
        timeMessage = await ctx.send("that took **0ms** to proccess")
        while True:

            def check(m):
                return m.author == ctx.author and (m.content.replace(" ", "").startswith("size=") or m.content.replace(" ", "").startswith("color=") or m.content.replace(" ", "").startswith("texture="))
                
            try:
                responseMessage = await self.bot.wait_for('message', timeout=120, check=check)
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
                    if ctx.author.avatar_url.endswith(".gif?size=1024"):
                        borderGen.GenerateGifWithTexture(filepath, texturePath, size)
                    else:
                        filepath = borderGen.GenerateWithTexture(filepath, texturePath, size)
                else:
                    if ctx.author.avatar_url.endswith(".gif?size=1024"):
                        borderGen.GenerateGif(filepath, color, size)
                    else:
                        filepath = borderGen.GenerateBasic(filepath, color, size)

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


def setup(bot):
    bot.add_cog(Border(bot))