import discord
from discord.ext import commands, tasks
import os
import aiohttp

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN مش موجود")

GAMES_CHANNEL_ID = 1473015187668861196
API_URL = "https://www.gamerpower.com/api/giveaways"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# نخزن ID العروض بدل الاسم (أدق)
sent_games = set()

# ========================
# 👑 نظام الأسماء (كما هو)
# ========================
@bot.event
async def on_member_join(member):
    try:
        base_name = member.display_name

        if "👑" in base_name:
            return

        new_name = f"👑 | {base_name} | 👑"

        if len(new_name) > 32:
            allowed_length = 32 - len("👑 |  | 👑")
            base_name = base_name[:allowed_length]
            new_name = f"👑 | {base_name} | 👑"

        await member.edit(nick=new_name)

    except:
        pass

# ========================
# 🎮 نظام العروض (يرسل فقط الجديد)
# ========================
@tasks.loop(minutes=5)
async def fetch_games():
    await bot.wait_until_ready()

    channel = bot.get_channel(GAMES_CHANNEL_ID)

    if channel is None:
        print("❌ الروم غير موجود")
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL) as resp:
                data = await resp.json()

                for game in data:
                    game_id = game.get("id")  # أهم شي
                    title = game.get("title")
                    url = game.get("open_giveaway_url")
                    image = game.get("image")
                    platforms = game.get("platforms", "")

                    if not game_id or not title or not url:
                        continue

                    # فقط Epic و Steam
                    if not ("Epic" in platforms or "Steam" in platforms):
                        continue

                    # ✅ إذا قديم → لا ترسل
                    if game_id in sent_games:
                        continue

                    # ✅ جديد → أرسل
                    sent_games.add(game_id)

                    embed = discord.Embed(
                        title=f"🎮 {title}",
                        description=f"📍 {platforms}\n[اضغط لتحميل اللعبة]({url})",
                        color=discord.Color.green()
                    )

                    if image:
                        embed.set_image(url=image)

                    await channel.send(embed=embed)

        except Exception as e:
            print(f"❌ Error: {e}")

# ========================
# READY
# ========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    if not fetch_games.is_running():
        fetch_games.start()

# ========================
# RUN
# ========================
bot.run(TOKEN)
