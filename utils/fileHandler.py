import aiofiles
import aiohttp
import os
import config
import logging
from io import BytesIO

image_format = config.image_format
formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def setup_logger(name, filename, level=logging.INFO):
    handler = logging.FileHandler(filename)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

async def download_avatar(author):
    if author.avatar is None:
        return
        
    filepath = "avatars/" + str(author.id) 
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    url = author.avatar_url_as(format=image_format, size=1024)
    if str(author.avatar_url).endswith(".gif?size=1024"):
        url = author.avatar_url
        filepath += f"/{author.avatar}.gif"
    else:
        filepath += f"/{author.avatar}.{image_format}"
    
    if os.path.isfile(filepath):
        return filepath

    await download_from_URL(filepath, str(url))
    return filepath

async def download_guild_icon(guild):
    if guild.icon is None:
        return

    url = guild.icon_url_as(format=image_format, size=128)
    
    filepath = f"guilds/{guild.id}.{image_format}"

    await download_from_URL(filepath, str(url))
    return filepath

async def setup_slideshow(guildId, urls):
    filepath = f'guilds/{guildId}'
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    clear_guild_folder(guildId)

    for i in range(len(urls)): 
        ext = (urls[i].split('.'))[-1]
        await download_from_URL(filepath + f'/{i}.{ext}', urls[i])

def clear_guild_folder(guildId):
    for filepath in get_filepaths(f'guilds/{guildId}/'):
        os.remove(filepath)

def clear_avatar_folder(userId):
    for filepath in get_filepaths(f'avatars/{userId}/'):
        os.remove(filepath)

def get_filepaths(filepath):
    filepaths = []
    for file in os.listdir(filepath):
        filepaths.append(filepath + file)
    filepaths.sort(key=os.path.getmtime)
    return filepaths

async def download_texture(filename, url):
    filepath = "textures/" + filename
    await download_from_URL(filepath, url)
    return filepath

async def save_image(filepath, fileBytes):
    fileBytes.seek(0)
    f = await aiofiles.open(filepath, mode='wb')
    await f.write(fileBytes.read())
    await f.close()

async def get_bytes_from_file(filepath):
    f = await aiofiles.open(filepath, mode='rb')
    return await f.read()

def create_folders():
    for filepath in config.filepaths:
        if not(os.path.exists(filepath)):
                os.mkdir(filepath)

async def get_command_count():
    async with aiofiles.open('logs/commands.log', mode='r') as f:
        lines = await f.readlines()
    return len(lines)

async def download_from_URL(filepath, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                f = await aiofiles.open(filepath, mode='wb')
                await f.write(await r.read())
                await f.close()

async def download_from_URL_to_bytesIO(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                image = BytesIO()
                image.write(await r.read())
                return image