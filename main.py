import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="f!", intents=intents)

@bot.event
async def on_ready():
    print(f"[OK] FUTROL BOT en linea como {bot.user}")
    print(f"[OK] Servidores activos: {len(bot.guilds)}")
    for guild in bot.guilds:
        nombre_seguro = guild.name.encode("ascii", "replace").decode("ascii")
        print(f"  -> {nombre_seguro} (ID: {guild.id})")

# Cargar modulos
async def load_cogs():
    cogs = ["penales", "impostor", "subasta", "trivia", "carrera", "reglas", "economia", "versus", "predicciones", "torneos"]
    for cog in cogs:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"[COG] OK: {cog}")
        except Exception as e:
            print(f"[COG] ERROR: {cog} -> {e}")

@bot.event
async def setup_hook():
    await load_cogs()
    # Sincroniza los comandos slash en TODOS los servidores al iniciar
    synced = await bot.tree.sync()
    print(f"[SYNC] {len(synced)} comandos sincronizados correctamente")

# Comando para re-sincronizar comandos en caliente (solo el dueno del bot)
@bot.command(name="sync")
@commands.is_owner()
async def sync_commands(ctx):
    synced = await bot.tree.sync()
    await ctx.send(f"OK: {len(synced)} comandos sincronizados.")

# Comando para recargar un modulo sin reiniciar el bot
# Uso: f!reload trivia
@bot.command(name="reload")
@commands.is_owner()
async def reload_cog(ctx, cog: str):
    try:
        await bot.reload_extension(f"cogs.{cog}")
        await ctx.send(f"OK: modulo `{cog}` recargado sin reiniciar el bot.")
    except Exception as e:
        await ctx.send(f"ERROR recargando `{cog}`: {e}")

bot.run(TOKEN)