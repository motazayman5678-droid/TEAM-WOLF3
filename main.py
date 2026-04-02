import discord
from discord.ext import commands, tasks
import os
import aiohttp
from datetime import date

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN مش موجود")

GAMES_CHANNEL_ID = 1473015187668861196
API_URL = "https://www.gamerpower.com/api/giveaways"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

sent_games = set()

# 📊 عداد يومي
daily_count = 0
current_day = date.today()

# ========================
# 👑 نظام الأسماء
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
# 🎮 نظام العروض (محدود يومياً)
# ========================
@tasks.loop(minutes=5)
async def fetch_games():
    global daily_count, current_day

    await bot.wait_until_ready()

    # 🔄 إعادة التصفير كل يوم
    if date.today() != current_day:
        daily_count = 0
        current_day = date.today()
        print("🔄 تم تصفير العداد اليومي")

    # ❌ إذا وصل الحد
    if daily_count >= 4:
        return

    channel = bot.get_channel(GAMES_CHANNEL_ID)

    if channel is None:
        print("❌ الروم غير موجود")
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL) as resp:
                data = await resp.json()

                for game in data:
                    if daily_count >= 4:
                        break

                    game_id = game.get("id")
                    title = game.get("title")
                    url = game.get("open_giveaway_url")
                    image = game.get("image")
                    platforms = game.get("platforms", "")

                    if not game_id or not title or not url:
                        continue

                    # فقط Epic و Steam
                    if not ("Epic" in platforms or "Steam" in platforms):
                        continue

                    if game_id in sent_games:
                        continue

                    # إرسال
                    sent_games.add(game_id)
                    daily_count += 1

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
