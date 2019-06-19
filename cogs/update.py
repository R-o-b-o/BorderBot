import asyncio
import aiohttp
import json

token = '575181ca402dbf1c95ff9f286a4e44d0bc52189f5b4b260953e340fc6e3c5dc02ca61333a2b476df0c4e79828bbce24168e6280b765af5fd5f90c5ee4482f443xxx'
# discord.py (rewrite) and Python 3.6+
# Cog example to update divinediscordbots server count
# You have to replace 'xxx' with your token

class Update: 

    def __init__(self, bot):
        self.bot = bot 
        self.session = aiohttp.ClientSession(loop=self.bot.loop) 

    async def update(self):
        guild_count = len(self.bot.guilds)
        payload = json.dumps({
        'server_count': guild_count
        })

        headers = {
            'authorization': token,
            'content-type': 'application/json'
        }

        url = 'https://divinediscordbots.com/bot/{}/stats'.format(self.bot.user.id)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            print('divinediscordbots statistics returned {} for {}'.format(resp.status, payload))

    async def on_guild_join(self, guild): 
        await self.update()

    async def on_guild_remove(self, guild): 
        await self.update()

    async def on_ready(self):
        await self.update()

def setup(bot):
    bot.add_cog(Update(bot))