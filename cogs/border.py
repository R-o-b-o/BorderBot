import discord
from discord.ext import commands
import math, asyncio, random, os
from io import BytesIO
from timeit import default_timer as timer
from utils import borderGen, fileHandler

async def send_preview_webhook(ctx, fileMessage, messageContent):
    try:
        webhook = await ctx.channel.create_webhook(name="BorderBot")
        await webhook.send(messageContent, avatar_url=fileMessage.attachments[0].url)
        await webhook.delete()
    except:
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            await ctx.send("If you want the preview, enable `manage webhooks` permission")
        else:
            await ctx.send("If you want the preview, use this command in a server")

def get_extension(filepath):
    return ".gif" if filepath.endswith(".gif") else ".png"

class Border(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='random', description='Generate a border with random parameters', usage="number of images to generate (max 5)", aliases=['randomBorder'])
    @commands.cooldown(1,10,commands.BucketType.guild)
    async def random_command(self, ctx, times : int=1):
        if  (times <= 3):
            await ctx.channel.trigger_typing()
            startTime = timer()
            
            for _ in range(0,times):
                filepath = await fileHandler.downloadAvatar(ctx.author)
                color = "#%06x" % random.randint(0, 0xFFFFFF)
                size = round(random.random() / 5 + 0.05, 4)
                fileBytes = await borderGen.GenerateBasic(filepath, color, size)
                
                await ctx.send(file=discord.File(fileBytes, filename=color + "-" + str(size) + ".png"))
            await ctx.send("that took **"+str(math.trunc((timer() - startTime) * 1000))+"** ms")
        else:
            await ctx.send("There is a maximun of 3, *sorry*")

    @commands.command(name='randomTexture', description='Generate a border with a random texture')
    @commands.cooldown(5,30,commands.BucketType.guild)
    async def randomTexture_command(self, ctx, size : float=0):
        await ctx.channel.trigger_typing()
        startTime = timer()
        texturepath = "textures/" + random.choice(os.listdir("textures/"))

        filepath = await fileHandler.downloadAvatar(ctx.author)

        if size == 0: size = random.random() / 5 + 0.05
        fileBytes = await borderGen.GenerateWithTexture(filepath, texturepath, size, colorSwap=True)

        fileMessage = await ctx.send(file=discord.File(fileBytes, filename=ctx.author.name + f" borderTextured{get_extension(filepath)}"))
        await send_preview_webhook(ctx, fileMessage, "that took **" + str(math.trunc((timer() - startTime) * 1000)) + "ms**")

    @commands.command(name='border', description='Add a single color border to your avatar', usage="(color) (decimal between 0 - 1) [defaults to size 0.1 and the most occuring color]")
    @commands.cooldown(2, 5,commands.BucketType.guild)
    async def border_command(self, ctx, color="default", size : float=0.1):
        await ctx.channel.trigger_typing()
        startTime = timer()

        filepath = await fileHandler.downloadAvatar(ctx.author)
            
        downloadTime = math.trunc((timer() - startTime) * 1000)
        startTime = timer()
                
        if color == "default":
            color = borderGen.GetMostFrequentColor(filepath)
        
        try:
            fileBytes = await borderGen.GenerateBasic(filepath, color, size)
        except ValueError:
            await ctx.send("I could not find color: **%s**\nFor the list of possible color names: https://www.w3schools.com/colors/colors_names.asp" % color)
            return

        processTime = math.trunc((timer() - startTime) * 1000)

        startTime = timer()
        fileMessage = await ctx.send(file=discord.File(fileBytes, filename=color + "-" + str(size) + get_extension(filepath)))
        uploadTime = math.trunc((timer() - startTime) * 1000)

        messageContent = "that took **%dms** to download, **%dms** to process, **%dms** to upload" % (downloadTime, processTime, uploadTime)
        await send_preview_webhook(ctx, fileMessage, messageContent)

    @commands.command(name='borderTexture', description='Add a textured border to your avatar', usage="(upload texture image) (decimal between 0 - 1) [defaults to size 0.1]")
    @commands.cooldown(2, 5,commands.BucketType.guild)
    async def borderTexture_command(self, ctx, size : float=0.1):
        await ctx.channel.trigger_typing()
        startTime = timer()

        if len(ctx.message.attachments) == 0:
            await ctx.send("I could not see a texture file, please upload one in your command message for it to work")
            return

        texturePath = await fileHandler.downloadTexture(ctx.message.attachments[0].filename, ctx.message.attachments[0].url)
        filepath = await fileHandler.downloadAvatar(ctx.author)
            
        downloadTime = math.trunc((timer() - startTime) * 1000)
        startTime = timer()
        
        fileBytes = await borderGen.GenerateWithTexture(filepath, texturePath, size)
        
        processTime = math.trunc((timer() - startTime) * 1000)
        startTime = timer()
        
            
        fileMessage = await ctx.send(file=discord.File(fileBytes, filename="Textured" + "-" + str(size) + get_extension(filepath)))
        uploadTime = math.trunc((timer() - startTime) * 1000)

        messageContent = "that took **%dms** to download, **%dms** to process, **%dms** to upload" % (downloadTime, processTime, uploadTime)
        await send_preview_webhook(ctx, fileMessage, messageContent)

    @commands.command(name='borderSquare', hidden=True)
    async def borderSquare(self, ctx, color="default", size : float=0.1):
        await ctx.channel.trigger_typing()
        startTime = timer()
        filepath = await fileHandler.downloadAvatar(ctx.author)
                
        downloadTime = math.trunc((timer() - startTime) * 1000)
        startTime = timer()
                    
        if color == "default":
            color = borderGen.GetMostFrequentColor(filepath)
            
        fileBytes = await borderGen.GenerateSquare(filepath, color, size)
            
        processTime = math.trunc((timer() - startTime) * 1000)
        startTime = timer()
                    
        fileMessage = await ctx.send(file=discord.File(fileBytes, filename=color + "-" + str(size) + ".png"))
        uploadTime = math.trunc((timer() - startTime) * 1000)

        messageContent = "that took **%dms** to download, **%dms** to process, **%dms** to upload" % (downloadTime, processTime, uploadTime)
        await send_preview_webhook(ctx, fileMessage, messageContent)

    @commands.command(name='editor', description='Lets you edit your border in real time!', aliases=['edit'])
    @commands.cooldown(1, 60,commands.BucketType.user)
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
                message = m.content.replace(" ", "").replace(self.bot.command_prefix, "").lower()
                return m.author == ctx.author and (message.startswith("size=") or message.startswith("color=") or message.startswith("texture=") or message=="close" or message=="save")
                
            try:
                responseMessage = await self.bot.wait_for('message', timeout=120, check=check)
            except asyncio.TimeoutError:
                await ctx.send("😿 **editor timed out** 😿")
                timedOut = True

            try:
                responseMessageContent = responseMessage.content.replace(" ", "").replace(self.bot.command_prefix, "").lower()
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
                    fileBytes = await borderGen.GenerateWithTexture(filepath, texturePath, size)
                else:
                    fileBytes = await borderGen.GenerateBasic(filepath, color, size)

                await imageMessage.delete()
                try:
                    await responseMessage.delete()
                except:
                    pass
                
                imageMessage = await ctx.send(file=discord.File(fileBytes, filename=color + "-" + str(size) + get_extension(filepath)))
            except:
                pass
        os.remove(filepath)

    @commands.command(name='colorswap', description="Use another avatar's color palette for your own", aliases=['palette', 'cs', 'colourswap'])
    async def palette(self, ctx, member : discord.Member = None):
        await ctx.channel.trigger_typing()
        filepathUser = await fileHandler.downloadAvatar(ctx.author)
        filepathOther = await fileHandler.downloadAvatar(member)

        fileBytes = await self.bot.loop.run_in_executor(None, borderGen.ColorSwap, filepathUser, filepathOther)
        file = discord.File(fileBytes, filename="palette"+ get_extension(filepathUser))
        await ctx.send(file=file)

def setup(bot):
    bot.add_cog(Border(bot))