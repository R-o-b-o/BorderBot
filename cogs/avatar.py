import discord
from discord.ext import commands
import os, random, math, asyncio
from timeit import default_timer as timer
from utils import fileHandler, borderGen

from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import load_model

model = load_model('anime_model.h5')

async def IsAnime(user):
    filepath = await fileHandler.downloadAvatar(user)
    img = load_img(filepath, target_size=(200, 200))
    img = img_to_array(img) / 255
    img = img.reshape(1, 200, 200, 3)
    return 1 - model.predict(img)[0][0]

class Avatar(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='avatar', description="Get a user's avatar", aliases=['pfp'], usage="[@user]")
    async def avatar(self, ctx, member : discord.Member = None):
        if member is None:
            member = ctx.author

        url = member.avatar_url_as(format='png', size=1024)
        if str(member.avatar_url).endswith(".gif?size=1024"):
            url = member.avatar_url
        
        color = borderGen.GetMostFrequentColor(await fileHandler.downloadAvatar(member))

        if random.randint(0, 5) == 0 and isinstance(ctx.channel, discord.abc.GuildChannel) and ctx.me.guild_permissions.manage_webhooks:
            embed=discord.Embed(description=f"[Avatar Link]({url})", color=int(color.replace('#', ''), 16))
            embed.set_thumbnail(url=url)
            embed.set_image(url=url)
            embed.set_author(name=f"{member.name}", icon_url=url)
            embed.set_footer(text=".", icon_url=url)

            webhook = await ctx.channel.create_webhook(name="BorderBot")
            await webhook.send(embed=embed, avatar_url=url)
            await webhook.delete()
        else:
            embed=discord.Embed(title=f"{member.name}", description=f"[Avatar Link]({url})", color=int(color.replace('#', ''), 16))
            embed.set_thumbnail(url=url)
            embed.set_image(url=url)
        
            await ctx.send(embed=embed)

    @commands.command(name='clearAvatarHistory', hidden=True, description='Remove all previous avatars', aliases=['removeHistory', 'clear'])
    @commands.cooldown(3,200,commands.BucketType.user)
    async def clearHistory(self, ctx):
        reactionMessage = await ctx.send("Are you sure you want to delete all your previous avatars?")
        await reactionMessage.add_reaction("❌")
        await reactionMessage.add_reaction("☑")

        def check(reaction, user):
            return user == ctx.author

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=10, check=check)

            if str(reaction.emoji) == '☑':
                fileHandler.clearAvatarFolder(ctx.author.id)
                await reactionMessage.edit(content="**All previous avatars cleared**")
            else:
                await reactionMessage.edit(content="**Command cancelled**")
        except asyncio.TimeoutError:
            await reactionMessage.edit(content="**Command timed out**")
        await reactionMessage.clear_reactions()

    @commands.command(name='history', description='See all previous avatars', aliases=['avatars'], usage="[@user]")
    @commands.cooldown(3,200,commands.BucketType.user)
    async def history(self, ctx, member : discord.Member = None):
        if member is None:
            member = ctx.author
        await ctx.channel.trigger_typing()
        startTime = timer()
        
        _ = await fileHandler.downloadAvatar(member)

        filepaths = fileHandler.getFilepaths("avatars/" + str(member.id) + "/")

        if len(filepaths) != 1:
            fileBytes = await borderGen.GetAvatarHistoryImage(filepaths)
            await ctx.send(f"processing **{len(filepaths)}** images took **{str(math.trunc((timer() - startTime) * 1000))}ms**", file=discord.File(fileBytes, filename="history.png"))

            reactionMessage = await ctx.send("Would you like me to dm you these individually?")
            await reactionMessage.add_reaction("❌")
            await reactionMessage.add_reaction("☑")

            def check(reaction, user):
                return user == ctx.author

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=10, check=check)

                if str(reaction.emoji) == '☑':
                    await reactionMessage.edit(content="Dmed previous avatars 🖼!")
                    await reactionMessage.clear_reactions()
                    
                    while (len(filepaths) != 0):
                        uploadSize = 0
                        filesToUpload = []
                        while(len(filesToUpload) < 10 and len(filepaths) != 0):
                            uploadSize += os.path.getsize(filepaths[-1])
                            if (uploadSize > 8*10**6):
                                break
                            else:
                                filesToUpload.append(discord.File(filepaths.pop()))
                        await ctx.author.send(files=filesToUpload)
                else:
                    await reactionMessage.delete()
            except asyncio.TimeoutError:
                await reactionMessage.delete()
        else:
            await ctx.send("There are no past avatars stored, try again next time you change it.")
    
    @commands.command(name='randomAvatar', description='View a random avatar')
    @commands.cooldown(10,30,commands.BucketType.user)
    async def randomAvatar(self, ctx):
        filepaths = []
        for path, _, files in os.walk("avatars/"):
            for name in files:
                filepaths.append(os.path.join(path, name))
        await ctx.send(file=discord.File(random.choice(filepaths)))

    @commands.command(name='colors', description='Get n most dominant avatar colors', aliases=['avatarcolours', 'avatarColors', 'colours'], usage="(# of colors)")
    @commands.cooldown(10,30,commands.BucketType.guild)
    async def avatarColors(self, ctx, numColors = 5):
        filepath = await fileHandler.downloadAvatar(ctx.author)
        fileBytes, colors = borderGen.GetDominantColorsImage(filepath, numColors)
        await ctx.send("```css\n"+', '.join(colors)+"\n```", file=discord.File(fileBytes, filename="colors.png"))

    @commands.command(name='weebcheck', description='Determine weebyness from your avatar', aliases=['weeb'], usage="[@user]")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def weebCheck(self, ctx, member : discord.Member = None):
        if member is None:
            member = ctx.author
        await ctx.channel.trigger_typing()

        weeb = await IsAnime(member) * 100

        if weeb >= 50:
            await ctx.send(f"I am **{weeb:.2f}%** sure {member.mention} is a weeb")
        else:
            await ctx.send(f"I am **{(100 - weeb):.2f}%** sure {member.mention} is not a weeb")


def setup(bot):
    bot.add_cog(Avatar(bot))