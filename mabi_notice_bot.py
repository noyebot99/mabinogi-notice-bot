import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = 1367107267744235521

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

last_notice_id = None

@bot.event
async def on_ready():
    print(f"✅ 로그인됨: {bot.user}")
    check_mabinogi_news.start()

@tasks.loop(minutes=1)
async def check_mabinogi_news():
    now = datetime.now()

    # ⏰ 매시간 정각(00분)에만 실행
    if now.minute != 0:
        return

    global last_notice_id

    url = "https://mabinogi.nexon.com/page/news/notice.asp"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="article")
    if not table:
        return

    first_notice = table.find("tr")
    if not first_notice:
        return

    num_cell = first_notice.find("td", class_="no")
    title_cell = first_notice.find("a")
    if not num_cell or not title_cell:
        return

    notice_id = num_cell.text.strip()
    title = title_cell.text.strip()
    link = "https://mabinogi.nexon.com" + title_cell["href"]

    if notice_id == last_notice_id:
        return

    last_notice_id = notice_id

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"📢 **[에린 소식]** 새 공지!\n**{title}**\n🔗 {link}")

bot.run(TOKEN)