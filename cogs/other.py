import discord
from discord.ext import commands
from timeit import default_timer as timer
import math, random, os
from utils import fileHandler, sql
import config

class Other(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ping', description="Find out bot's response time")
    async def ping(self, ctx):
        startTime = timer()
        m = await ctx.send(".")
        time = math.trunc((timer() - startTime) * 1000)
        await m.edit(content="that took **%dms**" % time)

    @commands.command(name='feedback', description="Give feedback to improve the bot's functionality", aliases=['question'], usage="(Feedback-Goes-Here)")
    @commands.cooldown(5,600,commands.BucketType.guild)
    async def feedback(self, ctx, *, feedback):
        if feedback is None:
            if random.randint(0, 2) == 0:
                await ctx.send("😡, It's blank you NONCE!")
            else:
                await ctx.send("😕, Is it in invisible ink?")
        else:
            await ctx.send("Thanks, if this is any good I'll give you some garlicoin")
            embed=discord.Embed(description=feedback, color=random.randint(0, 0xFFFFFF))
            embed.set_footer(text=f'From {ctx.author.name}')
            await self.bot.get_channel(560175720052293663).send(embed=embed)

    @commands.command(name='faq', description="Faq")
    @commands.cooldown(5,600,commands.BucketType.guild)
    async def faq(self, ctx):
        f = open("FAQ.md", "r")
        embed=discord.Embed(title="FAQ", description=f.read(), color=0xAD1457)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='stats', description="Bot stats")
    async def stats(self, ctx):
        await ctx.channel.trigger_typing()
        guilds = self.bot.guilds
        users = 0
        for guild in guilds:
            users += len(guild.members)

        commands = await fileHandler.GetNumberOfCommands()

        numAvatars = 0
        numUsers = 0
        _, dirs, files = next(os.walk("avatars/"))
        for _, dirs, files in os.walk("avatars/"):
            for _ in dirs:
                numUsers += 1
            for _ in files:
                numAvatars += 1
        
        statsMessage = ("I am in **%d** servers with **%d** users\n"
        "**%d** commands have been executed\n"
        "I also have **%d** avatars stored for **%d** users") % (len(guilds), users, commands, numAvatars, numUsers)
        await ctx.send(statsMessage)
    
    @commands.command(name='invite', description="Bot invite link", aliases=['link'], hidden=True)
    @commands.cooldown(1, 10,commands.BucketType.guild)
    async def invite(self, ctx):
        embed=discord.Embed(title="Bot Invite", description="https://discordapp.com/oauth2/authorize?&client_id=559008680268267528&scope=bot&permissions=536996960", color=0xAD1457)
        await ctx.send(embed=embed)
    
    @commands.command(name='vote', aliases=['upvote'], description="Links to vote for BorderBot")
    @commands.cooldown(1, 10,commands.BucketType.guild)
    async def vote(self, ctx):
        botListLinks = [("Divine Discord Bot List", "https://divinediscordbots.com/bot/559008680268267528/vote"), ('Botlist.Space', "https://botlist.space/bot/559008680268267528/upvote")]
        embed=discord.Embed(color=0xAD1457)
        for name, link in botListLinks:
            embed.add_field(name=name, value=link)
        
        await ctx.send(embed=embed)  

    @commands.command(name='prefix', description="Get or change the bot prefix", usage="[new prefix]")
    @commands.cooldown(1, 10,commands.BucketType.guild)
    async def prefix(self, ctx,  *, prefix='current'):
        if prefix != "current" and ctx.author.guild_permissions.manage_guild:
            await sql.ChangePrefix(ctx.guild.id, prefix)
        else:
            prefix = await sql.GetPrefixFromDb(ctx.guild.id) or config.prefix
        
        await ctx.send(f'The prefix is `{prefix}`')

    @commands.command(name='help', description="Help command")
    async def help(self, ctx, help_command="all"):
        prefix = (await self.bot.get_prefix(ctx.message))[2]

        if help_command == "all":
            embed=discord.Embed(color=0xAD1457)

            for cog in self.bot.cogs.keys():
                cog_commands = sorted(self.bot.get_cog(cog).get_commands(), key=lambda x: x.name)
                commands_str = ''
                for c in cog_commands:
                    if not c.hidden:
                        commands_str += f'**{c.name}** - *{c.description}*\n'

                if commands_str != '':
                    embed.add_field(name=cog, value=commands_str, inline=False)
                
            embed.add_field(name="Links",
                            value="""[Bot Invite](https://discordapp.com/oauth2/authorize?&client_id=559008680268267528&scope=bot&permissions=536987744)\n"""
                                  """[Support Server](https://discord.gg/Dy3anFM)""", inline=False)
            embed.set_footer(text=f"Type {prefix}help command for more info on a command.")
            await ctx.send(embed=embed)
        else:
            command = self.bot.get_command(help_command)

            names = ' | '.join([command.name]+command.aliases)
            names = f"[{names}]" if len(command.aliases) > 0 else names

            usage = "" if command.usage is None else f"`{command.usage}`"

            await ctx.send(f"**{prefix}{names}** {usage}")

def setup(bot):
    bot.add_cog(Other(bot))