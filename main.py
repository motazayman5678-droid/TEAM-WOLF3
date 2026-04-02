import discord
from discord.ext import commands, tasks
import os
import aiohttp

TOKEN = os.getenv("TOKEN")  # ضع توكن البوت هنا أو في Variables
GAMES_CHANNEL_ID = 1473015187668861196  # الروم المخصص للألعاب
API_URL = "https://www.gamerpower.com/api/giveaways"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# لتجنب إرسال نفس اللعبة أكثر من مرة
sent_games = set()

# ---------------------------
# تغيير اسم العضو عند الدخول
# ---------------------------
@bot.event
async def on_member_join(member):
    try:
        base_name = member.display_name
        # منع تكرار 👑
        if "👑" in base_name:
            return
        new_name = f"👑 | {base_name} | 👑"
        # الحد الأقصى 32 حرف
        if len(new_name) > 32:
            base_name = base_name[:20]
            new_name = f"👑 | {base_name} | 👑"
        await member.edit(nick=new_name)
    except discord.Forbidden:
        print(f"No permission to change nickname for {member.name}")
    except Exception as e:
        print(f"Error changing nickname: {e}")

# ---------------------------
# الألعاب المجانية التلقائية
# ---------------------------
@tasks.loop(minutes=60)  # يمكن تعديل الوقت حسب الرغبة
async def fetch_free_games():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL) as resp:
                data = await resp.json()
                channel = bot.get_channel(GAMES_CHANNEL_ID)
                for game in data:
                    title = game.get("title")
                    url = game.get("open_giveaway_url")
                    platforms = game.get("platforms")
                    if title and url and (title not in sent_games):
                        # فلترة Epic + Steam فقط
                        if "PC" in platforms:
                            sent_games.add(title)
                            text = f"🎮 **{title}**\n📍 Source: {platforms}\n🔗 Claim: {url}"
                            await channel.send(text)
        except Exception as e:
            print(f"Error fetching games: {e}")

@bot.event
async def on_ready():
    print(f"Bot is ready: {bot.user}")
    fetch_free_games.start()  # بدء التحقق التلقائي

bot.run(TOKEN)
