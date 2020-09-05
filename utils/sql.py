import aiosqlite
from asgiref.sync import async_to_sync
import os

db_filename = "BorderBot.sqlite"

@async_to_sync
async def create_db():
    if os.path.exists(db_filename):
        return

    sql_statements = ['CREATE TABLE Prefixes (GuildID INTEGER PRIMARY KEY, Prefix varchar(10))','CREATE TABLE IconChanger (GuildID INTEGER PRIMARY KEY, Interval int, ImageIndex int)']
    for statement in sql_statements: await execute_SQL(statement)

async def execute_SQL(sql, *params):
    async with aiosqlite.connect(db_filename) as db:
        await db.execute(sql, params)
        await db.commit()

async def execute_SQL_reader(sql, *params):
    async with aiosqlite.connect(db_filename) as db:
        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()
    return rows

async def get_prefix_from_DB(guild_id):
    prefix = await execute_SQL_reader('SELECT Prefix FROM Prefixes WHERE GuildID=?', guild_id)
    return prefix[0][0]
    
async def add_guilds(guild_ids):
    for guild_id in guild_ids:
        if (await execute_SQL_reader('SELECT NOT EXISTS (SELECT 1 FROM Prefixes WHERE GuildID=?)', guild_id))[0][0]:
            await AddGuild(guild_id)

async def AddIconChanger(guild_id, interval):
    await execute_SQL('INSERT OR REPLACE INTO IconChanger VALUES (?, ?, ?)', guild_id, interval, 0)

async def RemoveIconChanger(guild_id):
    await execute_SQL('DELETE FROM IconChanger WHERE GuildID=?', guild_id)

async def IncrementIconChanger(guild_ids):
    await execute_SQL(f"UPDATE IconChanger SET ImageIndex = ImageIndex + 1 WHERE GuildID in ({','.join([str(x) for x in guild_ids])})")

async def GetIconChanages():
    return await execute_SQL_reader('SELECT * FROM IconChanger')

async def ChangePrefix(guild_id, prefix):
    await execute_SQL('UPDATE Prefixes SET Prefix=? WHERE GuildID=?', prefix, guild_id)

async def AddGuild(guild_id):
    await execute_SQL('INSERT INTO Prefixes(GuildID) VALUES (?)', guild_id)

async def RemoveGuild(guild_id):
    await execute_SQL('DELETE FROM Prefixes    WHERE GuildID=?', guild_id)
    await execute_SQL('DELETE FROM IconChanger WHERE GuildID=?', guild_id)
