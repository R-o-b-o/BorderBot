import aiofiles
import aiohttp
import os

async def downloadAvatar(author):
    filepath = "avatars/" + str(author.id) 
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    url = str(author.avatar_url)

    if url.endswith(".gif?size=1024"):
        filepath += "/" + author.avatar + ".gif"
    else:
        filepath += "/" + author.avatar + ".webp"
    
    if os.path.isfile(filepath):
        return filepath

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                f = await aiofiles.open(filepath, mode='wb')
                await f.write(await r.read())
                await f.close()
    return filepath

async def downloadTexture(filename, url):
    filepath = "textures/" + filename
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                f = await aiofiles.open(filepath, mode='wb')
                await f.write(await r.read())
                await f.close()
    return filepath

async def saveImage(filepath, fileBytes):
    fileBytes.seek(0)
    f = await aiofiles.open(filepath, mode='wb')
    await f.write(fileBytes.read())
    await f.close()

async def CreateFolders():
    filepaths = ["avatars", "textures", "logs"]
    for filepath in filepaths:
        if not(os.path.exists(filepath)):
                os.mkdir(filepath)

async def GetNumberOfCommands():
    async with aiofiles.open('logs/commands.log', mode='r') as f:
        lines = await f.readlines()
    return len(lines)