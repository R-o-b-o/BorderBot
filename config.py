from os import environ as env
from dotenv import load_dotenv

load_dotenv()

token = env.get('TOKEN')
ddblToken = env.get('DDBLTOKEN')
blsToken = env.get('BLSTOKEN')

prefix =">"
imageFormat ="webp" #the static image format that the bot downloads and uploads
maxSize = (1024, 1024) #the maximum image size for the border image

cogs = [f'cogs.{cog}' for cog in ['avatar', 'border', 'other', 'guild', 'owner']]

filepaths = ["avatars", "textures", "logs", "guilds"]

support_guild = 558000276284506113
owner_id = 344270500987404288
