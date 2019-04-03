import discord
from discord.ext import commands
import math, asyncio, random, os
from timeit import default_timer as timer
import borderGen, fileHandler

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
                filepath = await fileHandler.downloadAvatar(ctx)
                fileBytes = borderGen.GenerateBasic(filepath, ("#%06x" % random.randint(0, 0xFFFFFF)), random.random() / 5 + 0.05)
                
                await ctx.send(file=discord.File(fileBytes, filename=ctx.author.name + " border.png"))
        else:
            await ctx.send("There is a maximun of 5, *sorry*")

    @commands.command(name='randomTexture', description='Generate a border with a random texture')
    @commands.cooldown(5,30)
    async def randomTexture_command(self, ctx):
        texturepath = "textures/" + random.choice(os.listdir("textures/"))

        filepath = await fileHandler.downloadAvatar(ctx)
        fileBytes = borderGen.GenerateWithTexture(filepath, texturepath, random.random() / 5 + 0.05)

        await ctx.send(file=discord.File(fileBytes, filename=ctx.author.name + " border.png"))

    @commands.command(name='border', description='Add a single color border to your avatar', usage="(color) (decimal between 0 - 1) [defaults to size 0.1 and the most occuring color]")
    @commands.cooldown(2, 5)
    async def border_command(self, ctx, color="default", size : float=0.1):
        try:
            startTime = timer()

            filepath = await fileHandler.downloadAvatar(ctx)
                
            downloadTime = math.trunc((timer() - startTime) * 1000)
            startTime = timer()
                    
            if color == "default":
                color = borderGen.GetMostFrequentColor(filepath)
            
            fileBytes = borderGen.GenerateBasic(filepath, color, size)
            
            processTime = math.trunc((timer() - startTime) * 1000)
            startTime = timer()
                    
            fileMessage = await ctx.send(file=discord.File(fileBytes, filename=ctx.author.name + " border.png"))
            uploadTime = math.trunc((timer() - startTime) * 1000)

            messageContent = "that took **%dms** to download, **%dms** to process, **%dms** to upload" % (downloadTime, processTime, uploadTime)
            try:
                webhook = await ctx.channel.create_webhook(name="BorderBot")
                await webhook.send(messageContent, avatar_url=fileMessage.attachments[0].url)
                await webhook.delete()
            except:
                await ctx.send(messageContent)
        except:
            await ctx.send("Invalid command, consider reading the **>help border**")

    @commands.command(name='editor', description='Lets you edit your border in real time!', aliases=['edit'])
    @commands.cooldown(1, 60)
    async def editor(self, ctx):
        filepath = await fileHandler.downloadAvatar(ctx)
        
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
                    
                    filepath = borderGen.GenerateWithTexture(filepath, texturePath, size)
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