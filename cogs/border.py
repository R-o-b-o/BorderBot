import discord
from discord.ext import commands
import math, asyncio, random, os
from io import BytesIO
from timeit import default_timer as timer
import borderGen, fileHandler

class Border(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='random', description='Generate a border with random parameters', usage="number of images to generate (max 5)", aliases=['randomBorder'])
    @commands.cooldown(5,30)
    async def random_command(self, ctx, times : int=1):
        if  (times <= 5):
            startTime = timer()
            
            for _ in range(0,times):
                filepath = await fileHandler.downloadAvatar(ctx.author)
                color = "#%06x" % random.randint(0, 0xFFFFFF)
                size = round(random.random() / 5 + 0.05, 4)
                fileBytes = borderGen.GenerateBasic(filepath, color, size)
                
                await ctx.send(file=discord.File(fileBytes, filename=color + "-" + str(size) + ".png"))
            await ctx.send("that took **"+str(math.trunc((timer() - startTime) * 1000))+"** ms")
        else:
            await ctx.send("There is a maximun of 5, *sorry*")

    @commands.command(name='randomTexture', description='Generate a border with a random texture')
    @commands.cooldown(5,30)
    async def randomTexture_command(self, ctx):
        texturepath = "textures/" + random.choice(os.listdir("textures/"))

        filepath = await fileHandler.downloadAvatar(ctx.author)
        fileBytes = borderGen.GenerateWithTexture(filepath, texturepath, random.random() / 5 + 0.05)

        await ctx.send(file=discord.File(fileBytes, filename=ctx.author.name + " borderTextured.png"))

    @commands.command(name='border', description='Add a single color border to your avatar', usage="(color) (decimal between 0 - 1) [defaults to size 0.1 and the most occuring color]")
    @commands.cooldown(2, 5)
    async def border_command(self, ctx, color="default", size : float=0.1):
        try:
            async with ctx.channel.typing():
                startTime = timer()

                filepath = await fileHandler.downloadAvatar(ctx.author)
                    
                downloadTime = math.trunc((timer() - startTime) * 1000)
                startTime = timer()
                        
                if color == "default":
                    color = borderGen.GetMostFrequentColor(filepath)
                
                fileBytes = borderGen.GenerateBasic(filepath, color, size)
                
                processTime = math.trunc((timer() - startTime) * 1000)
                startTime = timer()
                
                extension = ".png"
                if filepath.endswith(".gif"):
                    extension = ".gif"
                    
                fileMessage = await ctx.send(file=discord.File(fileBytes, filename=color + "-" + str(size) + extension))
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

    @commands.command(name='borderSquare', hidden=True)
    async def borderSquare(self, ctx, color="default", size : float=0.1):
        startTime = timer()
        filepath = await fileHandler.downloadAvatar(ctx.author)
                
        downloadTime = math.trunc((timer() - startTime) * 1000)
        startTime = timer()
                    
        if color == "default":
            color = borderGen.GetMostFrequentColor(filepath)
            
        fileBytes = borderGen.GenerateSquare(filepath, color, size)
            
        processTime = math.trunc((timer() - startTime) * 1000)
        startTime = timer()
                    
        fileMessage = await ctx.send(file=discord.File(fileBytes, filename=color + "-" + str(size) + ".png"))
        uploadTime = math.trunc((timer() - startTime) * 1000)

        messageContent = "that took **%dms** to download, **%dms** to process, **%dms** to upload" % (downloadTime, processTime, uploadTime)
        try:
            webhook = await ctx.channel.create_webhook(name="BorderBot")
            await webhook.send(messageContent, avatar_url=fileMessage.attachments[0].url)
            await webhook.delete()
        except:
            await ctx.send(messageContent)

    @commands.command(name='editor', description='Lets you edit your border in real time!', aliases=['edit'])
    @commands.cooldown(1, 60)
    async def editor(self, ctx):
        filepath = await fileHandler.downloadAvatar(ctx.author)
        
        await ctx.send("to change border say: (color = *color*) or (size = *decimal between 0 and 1*) or (texture = *upload texture image*)")
        await ctx.send("say **save** to work on another layer and **close** to end the editor")
        imageMessage = await ctx.send(file=discord.File(filepath))

        color = "red"
        size = 0.1
        fileBytes = BytesIO() 

        timedOut = False
        while not timedOut:

            def check(m):
                message = m.content.replace(" ", "").lower()
                return m.author == ctx.author and (message.startswith("size=") or message.startswith("color=") or message.startswith("texture=") or message=="close" or message=="save")
                
            try:
                responseMessage = await self.bot.wait_for('message', timeout=120, check=check)
            except asyncio.TimeoutError:
                await ctx.send("😿 **editor timed out** 😿")
                timedOut = True

            try:
                responseMessageContent = responseMessage.content.replace(" ", "").lower()
                if responseMessageContent.startswith("size="):
                    size = float(responseMessageContent.replace("size=", ""))
                elif responseMessageContent.startswith("color="):
                    color = responseMessageContent.replace("color=", "")
                    textured = False
                elif responseMessageContent == "save":
                    await fileHandler.saveImage(filepath, fileBytes)
                elif responseMessageContent == "close":
                    timedOut = True
                    await ctx.send("😻 **editor closed** 😻")
                elif responseMessageContent.startswith("texture="):
                    texturePath = await fileHandler.downloadTexture(responseMessage.attachments[0].filename, responseMessage.attachments[0].url)
                    textured = True
                    
                if textured:
                    fileBytes = borderGen.GenerateWithTexture(filepath, texturePath, size)
                else:
                    fileBytes = borderGen.GenerateBasic(filepath, color, size)

                await imageMessage.delete()
                try:
                    await responseMessage.delete()
                except:
                    pass
                
                imageMessage = await ctx.send(file=discord.File(fileBytes, filename=color + "-" + str(size) + ".png"))
            except:
                pass
        os.remove(filepath)


def setup(bot):
    bot.add_cog(Border(bot))