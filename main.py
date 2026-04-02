import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")  # حط التوكن في Variables

intents = discord.Intents.default()
intents.members = True  # مهم

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready: {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        # تنظيف الاسم عشان ما يتجاوز 32 حرف
        base_name = member.name
        new_name = f"👑 | {base_name} | 👑"

        if len(new_name) > 32:
            base_name = base_name[:20]
            new_name = f"👑 | {base_name} | 👑"

        await member.edit(nick=new_name)

    except discord.Forbidden:
        print(f"No permission to change nickname for {member.name}")
    except Exception as e:
        print(f"Error: {e}")

bot.run(TOKEN)
