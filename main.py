import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        new_name = f"👑 | {member.name} | 👑"
        await member.edit(nick=new_name)
    except Exception as e:
        print(f"Error: {e}")

bot.run(TOKEN)
