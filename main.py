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
        base_name = member.display_name

        # منع تكرار 👑
        if "👑" in base_name:
            return

        new_name = f"👑 | {base_name} | 👑"

        # التأكد من الطول
        if len(new_name) > 32:
            base_name = base_name[:20]
            new_name = f"👑 | {base_name} | 👑"

        await member.edit(nick=new_name)

    except discord.Forbidden:
        print("No permission")
    except Exception as e:
        print(e)

bot.run(TOKEN)
