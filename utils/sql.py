import aiosqlite
from asgiref.sync import async_to_sync
import os

dbFilename = "BorderBot.sqlite"

@async_to_sync
async def CreateDB():
    if os.path.exists(dbFilename):
        return

    sqlStatements = ['CREATE TABLE Prefixes (GuildID INTEGER PRIMARY KEY, Prefix varchar(10))','CREATE TABLE IconChanger (GuildID INTEGER PRIMARY KEY, Interval int, ImageIndex int)']
    for statement in sqlStatements: await ExecuteSQL(statement)

async def ExecuteSQL(sql, *params):
    async with aiosqlite.connect(dbFilename) as db:
        await db.execute(sql, params)
        await db.commit()

async def ExecuteSQLReader(sql, *params):
    async with aiosqlite.connect(dbFilename) as db:
        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()
    return rows

async def GetPrefixFromDb(guildId):
    prefix = await ExecuteSQLReader('SELECT Prefix FROM Prefixes WHERE GuildID=?', guildId)
    return prefix[0][0]
    
async def AddGuilds(guildIds):
    for guildId in guildIds:
        if (await ExecuteSQLReader('SELECT NOT EXISTS (SELECT 1 FROM Prefixes WHERE GuildID=?)', guildId))[0][0]:
            await AddGuild(guildId)

async def AddIconChanger(guildId, interval):
    await ExecuteSQL('INSERT OR REPLACE INTO IconChanger VALUES (?, ?, ?)', guildId, interval, 0)

async def RemoveIconChanger(guildId):
    await ExecuteSQL('DELETE FROM IconChanger WHERE GuildID=?', guildId)

async def IncrementIconChanger(guildIds):
    await ExecuteSQL(f"UPDATE IconChanger SET ImageIndex = ImageIndex + 1 WHERE GuildID in ({','.join([str(x) for x in guildIds])})")

async def GetIconChanages():
    return await ExecuteSQLReader('SELECT * FROM IconChanger')

async def ChangePrefix(guildId, prefix):
    await ExecuteSQL('UPDATE Prefixes SET Prefix=? WHERE GuildID=?', prefix, guildId)

async def AddGuild(guildId):
    await ExecuteSQL('INSERT INTO Prefixes(GuildID) VALUES (?)', guildId)

async def RemoveGuild(guildId):
    await ExecuteSQL('DELETE FROM Prefixes    WHERE GuildID=?', guildId)
    await ExecuteSQL('DELETE FROM IconChanger WHERE GuildID=?', guildId)