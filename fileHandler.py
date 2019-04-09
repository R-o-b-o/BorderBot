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

async def SetupLogging(filepath):
    if not(os.path.exists(filepath)):
        f = await aiofiles.open(filepath, mode='w')
        await f.write("0000-00-00 00:00:00 10 100")

async def CreateFolders():
    filepaths = ["avatars", "textures", "logs"]
    for filepath in filepaths:
        if not(os.path.exists(filepath)):
                os.mkdir(filepath)

async def GetNumberOfCommands():
    with open('logs/commands.log') as f:
            lines = f.readlines()
    return len(lines)