import aiofiles
import aiohttp
import os
import config
import logging

imageFormat = config.imageFormat
formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def setupLogger(name, filename, level=logging.INFO):
    handler = logging.FileHandler(filename)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

async def downloadAvatar(author):
    if author.avatar is None:
        return
        
    filepath = "avatars/" + str(author.id) 
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    url = author.avatar_url_as(format=imageFormat, size=1024)
    if str(author.avatar_url).endswith(".gif?size=1024"):
        url = author.avatar_url
        filepath += "/" + author.avatar + ".gif"
    else:
        filepath += "/" + author.avatar + f".{imageFormat}"
    
    if os.path.isfile(filepath):
        return filepath

    await downloadFromURL(filepath, str(url))
    return filepath

async def downloadGuildIcon(guild):
    if guild.icon is None:
        return

    url = guild.icon_url_as(format=imageFormat, size=128)
    
    filepath = f"guilds/{guild.id}.{imageFormat}"

    await downloadFromURL(filepath, str(url))
    return filepath

async def setupSlideshow(guildId, urls):
    filepath = f'guilds/{guildId}'
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    clearFolder(guildId)

    for i in range(len(urls)): 
        ext = (urls[i].split('.'))[-1]
        await downloadFromURL(filepath + f'/{i}.{ext}', urls[i])

def clearFolder(guildId):
    for filepath in getFilepaths(f'guilds/{guildId}/'):
        os.remove(filepath)

def getFilepaths(filepath):
    filepaths = []
    for file in os.listdir(filepath):
        filepaths.append(filepath + file)
    return filepaths

async def downloadTexture(filename, url):
    filepath = "textures/" + filename
    await downloadFromURL(filepath, url)
    return filepath

async def saveImage(filepath, fileBytes):
    fileBytes.seek(0)
    f = await aiofiles.open(filepath, mode='wb')
    await f.write(fileBytes.read())
    await f.close()

async def getFileBytesFromFile(filepath):
    f = await aiofiles.open(filepath, mode='rb')
    return await f.read()

def CreateFolders():
    for filepath in config.filepaths:
        if not(os.path.exists(filepath)):
                os.mkdir(filepath)

async def GetNumberOfCommands():
    async with aiofiles.open('logs/commands.log', mode='r') as f:
        lines = await f.readlines()
    return len(lines)

async def downloadFromURL(filepath, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                f = await aiofiles.open(filepath, mode='wb')
                await f.write(await r.read())
                await f.close()