import os
from dotenv import load_dotenv
from datetime import datetime
import discord
from discord import Embed
from discord.ext import commands
import time
from message_cls import DA

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@DA.csv_error_handler
def ran_today() -> bool:
    today = time.strftime("%y-%m-%d")
    with open("date_today.txt", "r") as fr:
        if fr.readline() == today:
            return True
    with open("date_today.txt", "w") as fw:
        fw.write(today)
    return False


@bot.event
async def on_ready():
    channel = bot.get_channel(1214521634606809121)
    embed = Embed(title="Daily announcement 📢", color=0x80cf4e, timestamp=datetime.now())
    name = DA.nameday_api_call()
    holiday = DA.holiday_api_call()
    weather = DA.weather_api_call()
    if name:
        embed_name = f"Meniny má:" if len(name.split(",")) == 1 else f"Meniny majú:"
        embed.add_field(name=embed_name, value=f"||*{name}*||", inline=False)
    else:
        name = DA.name_read_csv()
        if name:
            if len(name.split(" ")) == 1:
                embed_name = "Meniny má:"
            else:
                embed_name = "Meniny majú:"
                name = ", ".join(name.split(" "))
            embed.add_field(name=embed_name, value=f"||*{name}*||", inline=False)
    if holiday != "":
        embed_name = "Dnes je:"
        embed.add_field(name=embed_name, value=f"||{holiday}||", inline=False)
    elif holiday is None:
        holiday = DA.holiday_read_csv()
        if holiday:
            embed_name = "Dnes je:"
            embed.add_field(name=embed_name, value=f"||{holiday}||", inline=False)
    if weather:
        embed.add_field(name="Aktuálne počasie:", value=weather[0])
        embed.set_thumbnail(url=weather[1])
    embed.set_author(name=f"{bot.user.name}", icon_url=bot.user.display_avatar)

    await channel.send(embed=embed)

if __name__ == "__main__":
    if not ran_today():
       bot.run(TOKEN) 