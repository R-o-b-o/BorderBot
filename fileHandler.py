import aiofiles
import aiohttp
import os

async def downloadAvatar(ctx):
    filepath = "avatars/" + str(ctx.author.id) 
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    if ctx.author.avatar_url.endswith(".gif?size=1024"):
        filepath += "/" + ctx.author.avatar+ ".gif"
    else:
        filepath += "/" + ctx.author.avatar + ".webp"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(ctx.author.avatar_url) as r:
            if r.status == 200:
                f = await aiofiles.open(filepath, mode='wb')
                await f.write(await r.read())
                await f.close()
    return filepath