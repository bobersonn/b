import discord
from discord import app_commands
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class LegitBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.lc_channel_id = None
        self.welcome_channel_id = None
        self.lc_count = 0

bot = LegitBot()

# ====================== SETUP ======================
@bot.tree.command(name="setup", description="Konfiguracja bota (tylko admin)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    lc_channel="Kanał do legit checków",
    welcome_channel="Kanał powitalny"
)
async def setup(interaction: discord.Interaction, lc_channel: discord.TextChannel = None, welcome_channel: discord.TextChannel = None):
    if lc_channel:
        bot.lc_channel_id = lc_channel.id
    if welcome_channel:
        bot.welcome_channel_id = welcome_channel.id

    lc_ch = bot.get_channel(bot.lc_channel_id)
    welcome_ch = bot.get_channel(bot.welcome_channel_id)

    embed = discord.Embed(title="⚙️ Konfiguracja bota", color=0x7289da)
    embed.add_field(name="Kanał Legit Checki", value=lc_ch.mention if lc_ch else "Nie ustawiono", inline=False)
    embed.add_field(name="Kanał powitalny", value=welcome_ch.mention if welcome_ch else "Nie ustawiono", inline=False)
    embed.add_field(name="Liczba checków", value=str(bot.lc_count), inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# ====================== /LC ======================
@bot.tree.command(name="lc", description="Zgłoś item do legit checku")
@app_commands.describe(
    sprzedawca="Nazwa sprzedawcy / nick / link",
    co="Co sprzedaje (model, nazwa itemu)",
    ile="Ilość sztuk",
    cena="Cena w PLN"
)
async def lc(interaction: discord.Interaction, sprzedawca: str, co: str, ile: int, cena: int):
    bot.lc_count += 1

    embed = discord.Embed(title="🛍️ Nowy  Legit Check", color=0x00ff00, timestamp=datetime.now())
    embed.add_field(name="Sprzedawca", value=sprzedawca, inline=False)
    embed.add_field(name="Przedmiot", value=co, inline=False)
    embed.add_field(name="Ilość", value=f"{ile} szt.", inline=True)
    embed.add_field(name="Cena", value=f"{cena:,} PLN".replace(",", " "), inline=True)
    embed.add_field(name="wystawił", value=interaction.user.mention, inline=False)
    embed.set_footer(text=f"Legit check #{bot.lc_count}")

    if bot.lc_channel_id:
        lc_channel = bot.get_channel(bot.lc_channel_id)
        if lc_channel:
            await lc_channel.send(embed=embed)
            try:
                await lc_channel.edit(name=f"legit-checki-{bot.lc_count}")
            except:
                pass
            return await interaction.response.send_message("✅ Zgłoszenie wysłane!", ephemeral=True)

    await interaction.response.send_message("❌ Najpierw ustaw kanał komendą `/setup`", ephemeral=True)

# ====================== POWITANIE ======================
@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(bot.welcome_channel_id) or member.guild.system_channel
    if channel:
        embed = discord.Embed(title="👋 Witaj!", description=f"{member.mention} dołączył!", color=0x7289da)
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Bot online! {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Legit Checki"))
    await bot.tree.sync()
    print("Slash commands zsynchronizowane!")

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("Brak tokena w .env!")
else:
    bot.run(TOKEN)
