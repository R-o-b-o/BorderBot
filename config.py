from os import environ as env
from dotenv import load_dotenv

load_dotenv()

token = env.get('TOKEN')
prefix =">"
imageFormat ="webp" #the static image format that the bot downloads and uploads

cogs = ['cogs.avatar', 'cogs.border', 'cogs.other']

support_guild = 410488579140354049
owner_id = 344270500987404288
