import discord
from discord.ext import commands
import math, asyncio, random, os
from io import BytesIO
from timeit import default_timer as timer
from utils import borderGen, fileHandler

def get_extension(filepath):
    return ".gif" if filepath.endswith(".gif") else ".png"

class Border(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.bot_icon_bytes = None

    async def get_bot_icon(self):
        if self.bot_icon_bytes is None:
            self.bot_icon_bytes = await fileHandler.download_from_URL_to_bytesIO(str(self.bot.user.avatar_url_as(format="png", size=128)))
        self.bot_icon_bytes.seek(0)
        return self.bot_icon_bytes

    async def send_preview_webhook(self, ctx, fileMessage, messageContent):
        try:
            preview_webhook = None
            for webhook in await ctx.channel.webhooks():
                if webhook.user.id == self.bot.user.id:
                    preview_webhook = webhook

            if not preview_webhook:
                preview_webhook = await ctx.channel.create_webhook(name="BorderBot", avatar=(await self.get_bot_icon()).read())


            await preview_webhook.send(messageContent, username=ctx.guild.get_member(self.bot.user.id).display_name, avatar_url=fileMessage.attachments[0].url)
            #await webhook.delete()
        except:
            if isinstance(ctx.channel, discord.abc.GuildChannel):
                await ctx.send("If you want the preview, enable `manage webhooks` permission")
            else:
                await ctx.send("If you want the preview, use this command in a server")

    @commands.command(name='random', description='Generate a border with random parameters', usage="(# images {max 5})", aliases=['randomBorder'])
    @commands.cooldown(2,10,commands.BucketType.user)
    async def random_command(self, ctx, times : int=1):
        if  (times <= 3):
            await ctx.channel.trigger_typing()
            start_time = timer()
            
            for _ in range(0,times):
                filepath = await fileHandler.download_avatar(ctx.author)
                color = "#%06x" % random.randint(0, 0xFFFFFF)
                size = round(random.random() / 5 + 0.05, 4)
                file_bytes = await borderGen.generate_basic(filepath, color, size)
                
                await ctx.send(file=discord.File(file_bytes, filename=color + "-" + str(size) + ".png"))
            await ctx.send("that took **"+str(math.trunc((timer() - start_time) * 1000))+"** ms")
        else:
            await ctx.send("There is a maximun of 3, *sorry*")

    @commands.command(name='randomTexture', description='Generate a border with a random texture')
    @commands.cooldown(5,30,commands.BucketType.guild)
    async def randomTexture_command(self, ctx, size : float=0):
        await ctx.channel.trigger_typing()
        start_time = timer()
        texturepath = "textures/" + random.choice(os.listdir("textures/"))

        filepath = await fileHandler.download_avatar(ctx.author)

        if size == 0: size = random.random() / 5 + 0.05
        file_bytes = await borderGen.generate_textured(filepath, texturepath, size, colorSwap=True)

        file_msg = await ctx.send(file=discord.File(file_bytes, filename=ctx.author.name + f" borderTextured{get_extension(filepath)}"))
        await self.send_preview_webhook(ctx, file_msg, "that took **" + str(math.trunc((timer() - start_time) * 1000)) + "ms**")

    @commands.command(name='border', description='Add a single color border', usage="(color) (decimal between 0-1) <defaults to size 0.1 and the most occuring color>", aliases=["b"])
    @commands.cooldown(2, 5,commands.BucketType.guild)
    async def border_command(self, ctx, color="default", size : float=0.1):
        await ctx.channel.trigger_typing()
        start_time = timer()

        filepath = await fileHandler.download_avatar(ctx.author)
            
        download_time = math.trunc((timer() - start_time) * 1000)
        start_time = timer()
                
        if color == "default":
            color = random.choice(borderGen.get_dominant_colors(filepath, 10))
        
        try:
            file_bytes = await borderGen.generate_basic(filepath, color, size)
        except ValueError:
            await ctx.send("I could not find color: **%s**\nFor the list of possible color names: https://www.w3schools.com/colors/colors_names.asp" % color)
            return

        process_time = math.trunc((timer() - start_time) * 1000)

        start_time = timer()
        file_msg = await ctx.send(file=discord.File(file_bytes, filename=color + "-" + str(size) + get_extension(filepath)))
        upload_time = math.trunc((timer() - start_time) * 1000)

        msg_content = "that took **%dms** to download, **%dms** to process, **%dms** to upload" % (download_time, process_time, upload_time)
        await self.send_preview_webhook(ctx, file_msg, msg_content)

    @commands.command(name='borderTexture', description='Add a textured border', usage="(upload texture image) (decimal between 0-1) <defaults to size 0.1>", aliases=['bt'])
    @commands.cooldown(2, 5,commands.BucketType.guild)
    async def borderTexture_command(self, ctx, size : float=0.1):
        await ctx.channel.trigger_typing()
        start_time = timer()

        if len(ctx.message.attachments) == 0:
            await ctx.send("I could not see a texture file, please upload one in your command message for it to work")
            return

        texturePath = await fileHandler.download_texture(ctx.message.attachments[0].filename, ctx.message.attachments[0].url)
        filepath = await fileHandler.download_avatar(ctx.author)
            
        download_time = math.trunc((timer() - start_time) * 1000)
        start_time = timer()
        
        file_bytes = await borderGen.generate_textured(filepath, texturePath, size)
        
        process_time = math.trunc((timer() - start_time) * 1000)
        start_time = timer()
        
            
        file_msg = await ctx.send(file=discord.File(file_bytes, filename="Textured" + "-" + str(size) + get_extension(filepath)))
        upload_time = math.trunc((timer() - start_time) * 1000)

        msg_content = "that took **%dms** to download, **%dms** to process, **%dms** to upload" % (download_time, process_time, upload_time)
        await self.send_preview_webhook(ctx, file_msg, msg_content)

    @commands.command(name='borderSquare', hidden=True)
    @commands.cooldown(5,30,commands.BucketType.guild)
    async def borderSquare(self, ctx, color="default", size : float=0.1):
        await ctx.channel.trigger_typing()
        start_time = timer()
        filepath = await fileHandler.download_avatar(ctx.author)
                
        download_time = math.trunc((timer() - start_time) * 1000)
        start_time = timer()
                    
        if color == "default":
            color = borderGen.get_most_frequent_color(filepath)
            
        file_bytes = await borderGen.generate_square(filepath, color, size)
            
        process_time = math.trunc((timer() - start_time) * 1000)
        start_time = timer()
                    
        file_msg = await ctx.send(file=discord.File(file_bytes, filename=color + "-" + str(size) + ".png"))
        upload_time = math.trunc((timer() - start_time) * 1000)

        msg_content = "that took **%dms** to download, **%dms** to process, **%dms** to upload" % (download_time, process_time, upload_time)
        await self.send_preview_webhook(ctx, file_msg, msg_content)

    @commands.command(name='editor', description='Lets you edit your border in real time!', aliases=['edit'], hidden=True)
    @commands.cooldown(1, 60,commands.BucketType.user)
    async def editor(self, ctx):
        filepath = await fileHandler.download_avatar(ctx.author)
        
        await ctx.send("to change border say: (color = *color*) or (size = *decimal between 0 and 1*) or (texture = *upload texture image*)")
        await ctx.send("say **save** to work on another layer and **close** to end the editor")
        image_msg = await ctx.send(file=discord.File(filepath))

        color = "red"
        size = 0.1
        file_bytes = BytesIO() 

        timed_out = False
        while not timed_out:

            def check(m):
                message = m.content.replace(" ", "").replace(self.bot.command_prefix, "").lower()
                return m.author == ctx.author and (message.startswith("size=") or message.startswith("color=") or message.startswith("texture=") or message=="close" or message=="save")
                
            try:
                response_msg = await self.bot.wait_for('message', timeout=120, check=check)
            except asyncio.TimeoutError:
                await ctx.send("😿 **editor timed out** 😿")
                timed_out = True

            try:
                response_msg_content = response_msg.content.replace(" ", "").replace(self.bot.command_prefix, "").lower()
                if response_msg_content.startswith("size="):
                    size = float(response_msg_content.replace("size=", ""))
                elif response_msg_content.startswith("color="):
                    color = response_msg_content.replace("color=", "")
                    textured = False
                elif response_msg_content == "save":
                    await fileHandler.save_image(filepath, file_bytes)
                elif response_msg_content == "close":
                    timed_out = True
                    await ctx.send("😻 **editor closed** 😻")
                elif response_msg_content.startswith("texture="):
                    texturePath = await fileHandler.download_texture(response_msg.attachments[0].filename, response_msg.attachments[0].url)
                    textured = True
                    
                if textured:
                    file_bytes = await borderGen.generate_textured(filepath, texturePath, size)
                else:
                    file_bytes = await borderGen.generate_basic(filepath, color, size)

                await image_msg.delete()
                try:
                    await response_msg.delete()
                except:
                    pass
                
                image_msg = await ctx.send(file=discord.File(file_bytes, filename=color + "-" + str(size) + get_extension(filepath)))
            except:
                pass
        os.remove(filepath)

    @commands.command(name='colorswap', description="Use another avatar's color palette on your own", aliases=['palette', 'cs', 'colourswap'], usage="@user")
    @commands.cooldown(5,20,commands.BucketType.guild)
    async def palette(self, ctx, member : discord.Member = None):
        await ctx.channel.trigger_typing()
        filepath_user = await fileHandler.download_avatar(ctx.author)
        if member is None:
            filepath_other = await fileHandler.download_from_URL_to_bytesIO(ctx.message.attachments[0].url)
        else:
            filepath_other = await fileHandler.download_avatar(member)

        file_bytes = await self.bot.loop.run_in_executor(None, borderGen.color_swap, filepath_user, filepath_other)
        file = discord.File(file_bytes, filename="palette"+ get_extension(filepath_user))
        await ctx.send(file=file)

def setup(bot):
    bot.add_cog(Border(bot))