import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import music

cogs = [music]

client = commands.Bot(command_prefix='?', intents=discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

load_dotenv()
client.run(os.getenv("TOKEN"))
