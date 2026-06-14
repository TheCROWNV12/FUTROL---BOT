# cogs/subasta.py
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from utils import db

import math

JUGADORES = [
    {"nombre": "Lionel Messi", "posicion": "DEL", "ovr": 95, "emoji": "🐐", "pais": "🇦🇷"},
    {"nombre": "Cristiano Ronaldo", "posicion": "DEL", "ovr": 93, "emoji": "🇵🇹", "pais": "🇵🇹"},
    {"nombre": "Kylian Mbappé", "posicion": "DEL", "ovr": 92, "emoji": "⚡", "pais": "🇫🇷"},
    {"nombre": "Vinicius Jr", "posicion": "EXT", "ovr": 90, "emoji": "🎭", "pais": "🇧🇷"},
    {"nombre": "Erling Haaland", "posicion": "DEL", "ovr": 91, "emoji": "🏔️", "pais": "🇳🇴"},
    {"nombre": "Jude Bellingham", "posicion": "MC", "ovr": 89, "emoji": "👑", "pais": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    {"nombre": "Kevin De Bruyne", "posicion": "MC", "ovr": 91, "emoji": "🎯", "pais": "🇧🇪"},
    {"nombre": "Luka Modrić", "posicion": "MC", "ovr": 88, "emoji": "🇭🇷", "pais": "🇭🇷"},
    {"nombre": "Neymar Jr", "posicion": "EXT", "ovr": 89, "emoji": "🤙", "pais": "🇧🇷"},
    {"nombre": "Robert Lewandowski", "posicion": "DEL", "ovr": 90, "emoji": "🇵🇱", "pais": "🇵🇱"},
    {"nombre": "Harry Kane", "posicion": "DEL", "ovr": 90, "emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "pais": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    {"nombre": "Mohamed Salah", "posicion": "EXT", "ovr": 89, "emoji": "🇪🇬", "pais": "🇪🇬"},
    {"nombre": "Antoine Griezmann", "posicion": "DEL", "ovr": 88, "emoji": "🇫🇷", "pais": "🇫🇷"},
    {"nombre": "Virgil van Dijk", "posicion": "DFC", "ovr": 90, "emoji": "🧱", "pais": "🇳🇱"},
    {"nombre": "Thibaut Courtois", "posicion": "POR", "ovr": 90, "emoji": "🧤", "pais": "🇧🇪"},
    {"nombre": "Marc-André ter Stegen", "posicion": "POR", "ovr": 89, "emoji": "🧤", "pais": "🇩🇪"},
    {"nombre": "Rodri", "posicion": "MCD", "ovr": 91, "emoji": "🛡️", "pais": "🇪🇸"},
    {"nombre": "Toni Kroos", "posicion": "MC", "ovr": 88, "emoji": "🇩🇪", "pais": "🇩🇪"},
    {"nombre": "Zinedine Zidane", "posicion": "MC", "ovr": 94, "emoji": "🎩", "pais": "🇫🇷"},
    {"nombre": "Pelé", "posicion": "DEL", "ovr": 98, "emoji": "👑", "pais": "🇧🇷"},
    {"nombre": "Diego Maradona", "posicion": "MCO", "ovr": 97, "emoji": "🔟", "pais": "🇦🇷"},
    {"nombre": "Ronaldinho", "posicion": "EXT", "ovr": 94, "emoji": "🤙", "pais": "🇧🇷"},
    {"nombre": "Luis Suárez", "posicion": "DEL", "ovr": 87, "emoji": "🔫", "pais": "🇺🇾"},
    {"nombre": "Karim Benzema", "posicion": "DEL", "ovr": 89, "emoji": "🇫🇷", "pais": "🇫🇷"},
    {"nombre": "Lautaro Martínez", "posicion": "DEL", "ovr": 88, "emoji": "🐂", "pais": "🇦🇷"}
]


def obtener_rareza(jugador):
    ovr = jugador["ovr"]
    if ovr >= 93:
        return "✨ **ORO** ✨", 0xFFD700, 800
    elif ovr >= 88:
        return "🥈 **PLATA** 🥈", 0xC0C0C0, 400
    else:
        return "🥉 **BRONCE** 🥉", 0xCD7F32, 100

class SubastaButtons(discord.ui.View):
    def __init__(self, subasta_cog, message=None):
        super().__init__(timeout=80)
        self.subasta_cog = subasta_cog
        self.message = message

    async def on_timeout(self):
        # Cuando expira la vista, si la subasta sigue activa, cerrarla
        if self.subasta_cog.subasta_activa:
            await self.subasta_cog.cerrar_subasta()

    async def proccess_bid(self, interaction: discord.Interaction, puja_extra: int):
        if not self.subasta_cog.subasta_activa:
            await interaction.response.send_message("❌ Esta subasta ya ha finalizado.", ephemeral=True)
            return

        user = interaction.user
        saldo = db.get_saldo(user.id)
        nueva_oferta = self.subasta_cog.mejor_oferta + puja_extra

        # Validaciones de saldo y apuestas
        if nueva_oferta > saldo:
            await interaction.response.send_message(f"❌ No tienes suficientes monedas. Tu saldo actual: `{saldo}💰`.", ephemeral=True)
            return

        if self.subasta_cog.mejor_postor and user.id == self.subasta_cog.mejor_postor.id:
            await interaction.response.send_message("⚠️ Ya eres el postor más alto en este momento.", ephemeral=True)
            return

        # Actualizar datos de subasta
        self.subasta_cog.mejor_oferta = nueva_oferta
        self.subasta_cog.mejor_postor = user

        # Reiniciar el tiempo de la subasta a 15 segundos si quedaba menos de ese tiempo (snipe protection!)
        if self.subasta_cog.tiempo_restante < 15:
            self.subasta_cog.tiempo_restante = 15

        # Confirmar en chat y actualizar el embed principal
        await interaction.response.send_message(f"💰 {user.mention} subió la puja en **+{puja_extra} monedas** (Total: `{nueva_oferta} monedas` 💰)")
        await self.subasta_cog.update_embed()

    @discord.ui.button(label="+100 💰", style=discord.ButtonStyle.success, custom_id="bid_100")
    async def bid_100(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.proccess_bid(interaction, 100)

    @discord.ui.button(label="+500 💰", style=discord.ButtonStyle.success, custom_id="bid_500")
    async def bid_500(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.proccess_bid(interaction, 500)

    @discord.ui.button(label="+1000 💰", style=discord.ButtonStyle.success, custom_id="bid_1000")
    async def bid_1000(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.proccess_bid(interaction, 1000)

    @discord.ui.button(label="Comando /apostar ✏️", style=discord.ButtonStyle.secondary, custom_id="bid_info", disabled=True)
    async def bid_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Deshabilitado por diseño, sirve de aviso visual
        pass


class Subasta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.subasta_activa = False
        self.jugador_actual = None
        self.mejor_oferta = 0
        self.mejor_postor = None
        self.tiempo_restante = 60
        self.subasta_msg = None
        self.view = None
        self.precio_minimo = 0

    async def update_embed(self):
        if not self.subasta_msg:
            return

        rareza_texto, rareza_color, precio_min = obtener_rareza(self.jugador_actual)
        embed = discord.Embed(
            title="🔮 SUBASTA FUTBOLERA — FUTROL",
            description=f"¡Un jugador misterioso está en subasta!\nRareza: {rareza_texto}",
            color=rareza_color
        )
        embed.add_field(name="❓ Jugador", value="**❓ ??? ❓**\n*Solo la silueta y nacionalidad están visibles*", inline=False)
        embed.add_field(name="Posición", value=f"|| {self.jugador_actual['posicion']} ||", inline=True)
        embed.add_field(name="Nacionalidad", value=f"{self.jugador_actual['pais']}", inline=True)
        embed.add_field(name="OVR (Media)", value=f"|| {self.jugador_actual['ovr']} ||", inline=True)
        embed.add_field(name="Rareza", value=rareza_texto, inline=True)
        embed.add_field(name="💰 Precio Mínimo", value=f"`{precio_min} monedas`", inline=True)
        
        postor_texto = self.mejor_postor.mention if self.mejor_postor else "Nadie"
        embed.add_field(name="💰 Puja Más Alta", value=f"`{self.mejor_oferta} monedas`", inline=True)
        embed.add_field(name="👑 Líder de Puja", value=postor_texto, inline=True)
        
        embed.set_footer(text=f"Tiempo restante: aprox {self.tiempo_restante} segundos • FUTROL")

        try:
            await self.subasta_msg.edit(embed=embed, view=self.view)
        except Exception:
            pass

    @app_commands.command(name="subasta", description="🔮 Iniciar la subasta de un jugador misterioso")
    async def subasta(self, interaction: discord.Interaction):
        if self.subasta_activa:
            await interaction.response.send_message("⚠️ Ya hay una subasta activa. Usa los botones del mensaje o `/apostar`.")
            return

        # Inicialización
        self.jugador_actual = random.choice(JUGADORES)
        self.subasta_activa = True
        self.mejor_oferta = 0
        self.mejor_postor = None
        self.tiempo_restante = 60

        rareza_texto, rareza_color, precio_min = obtener_rareza(self.jugador_actual)
        self.precio_minimo = precio_min
        self.mejor_oferta = precio_min

        embed = discord.Embed(
            title="🔮 SUBASTA FUTBOLERA — FUTROL",
            description=f"¡Un jugador misterioso está en subasta!\nRareza: {rareza_texto}",
            color=rareza_color
        )
        embed.add_field(name="❓ Jugador", value="**❓ ??? ❓**\n*Solo la silueta y nacionalidad están visibles*", inline=False)
        embed.add_field(name="Posición", value=f"|| {self.jugador_actual['posicion']} ||", inline=True)
        embed.add_field(name="Nacionalidad", value=f"{self.jugador_actual['pais']}", inline=True)
        embed.add_field(name="OVR (Media)", value=f"|| {self.jugador_actual['ovr']} ||", inline=True)
        embed.add_field(name="Rareza", value=rareza_texto, inline=True)
        embed.add_field(name="💰 Precio Mínimo", value=f"`{precio_min} monedas`", inline=True)
        embed.add_field(name="💰 Puja Más Alta", value=f"`{precio_min} monedas`", inline=True)
        embed.add_field(name="👑 Líder de Puja", value="Nadie", inline=True)
        embed.set_footer(text="Tiempo restante: 60 segundos • FUTROL")

        self.view = SubastaButtons(self)
        await interaction.response.send_message(embed=embed, view=self.view)
        self.subasta_msg = await interaction.original_response()
        self.view.message = self.subasta_msg

        # Bucle de cuenta regresiva
        while self.tiempo_restante > 0 and self.subasta_activa:
            await asyncio.sleep(5)
            self.tiempo_restante -= 5
            if self.subasta_activa:
                await self.update_embed()

        if self.subasta_activa:
            await self.cerrar_subasta()

    @app_commands.command(name="apostar", description="💰 Hacer una oferta personalizada en la subasta activa")
    async def apostar(self, interaction: discord.Interaction, cantidad: int):
        if not self.subasta_activa:
            await interaction.response.send_message("❌ No hay ninguna subasta activa en este momento.", ephemeral=True)
            return

        if cantidad <= self.mejor_oferta:
            await interaction.response.send_message(f"❌ Tu oferta debe superar la puja actual de `{self.mejor_oferta} monedas`.", ephemeral=True)
            return

        user = interaction.user
        saldo = db.get_saldo(user.id)

        if cantidad > saldo:
            await interaction.response.send_message(f"❌ No tienes suficientes monedas. Tu saldo actual: `{saldo}💰`.", ephemeral=True)
            return

        if self.mejor_postor and user.id == self.mejor_postor.id:
            await interaction.response.send_message("⚠️ Ya eres el postor más alto en este momento.", ephemeral=True)
            return

        # Guardar la nueva puja
        self.mejor_oferta = cantidad
        self.mejor_postor = user

        # Snipe protection: si queda poco tiempo, extender a 15 segundos
        if self.tiempo_restante < 15:
            self.tiempo_restante = 15

        await interaction.response.send_message(f"💰 {user.mention} apostó **{cantidad} monedas** directamente — ¡Nuevo líder!")
        await self.update_embed()

    async def cerrar_subasta(self):
        self.subasta_activa = False

        # Deshabilitar botones de la vista
        if self.view:
            for child in self.view.children:
                child.disabled = True
            try:
                await self.subasta_msg.edit(view=self.view)
            except Exception:
                pass

        if not self.mejor_postor:
            embed = discord.Embed(
                title="⏰ SUBASTA TERMINADA",
                description="Ningún usuario ofertó por el jugador misterioso. La subasta ha expirado sin ganador.",
                color=0xE74C3C
            )
            await self.subasta_msg.channel.send(embed=embed)
            return

        # Procesar ganador en la base de datos
        ganador_id = self.mejor_postor.id

        # Check for auction boost item
        data_ganador = db.get_user(ganador_id)
        tiene_boost = "boost_subasta" in data_ganador.get("items", [])
        if tiene_boost:
            db.remove_item(ganador_id, "boost_subasta")

        db.sub_saldo(ganador_id, self.mejor_oferta)
        db.add_jugador(ganador_id, self.jugador_actual)

        # Track subastas ganadas for insignia
        subastas = data_ganador.get("subastas_ganadas", 0) + 1
        db.update_user(ganador_id, subastas_ganadas=subastas)

        # Check for subasta_rey insignia
        if subastas >= 3:
            db.add_insignia(ganador_id, "subasta_rey")

        nuevo_saldo = db.get_saldo(ganador_id)

        premio_extra = "+ 500💰 (Boost de Subasta)" if tiene_boost else ""
        if tiene_boost:
            db.add_saldo(ganador_id, 500)

        rareza_texto, _, _ = obtener_rareza(self.jugador_actual)
        embed = discord.Embed(
            title="🏆 ¡SUBASTA TERMINADA Y ADQUIRIDA!",
            description=f"¡Felicidades a {self.mejor_postor.mention} por asegurar la puja!\nRareza: {rareza_texto}",
            color=0x2ECC71
        )
        embed.add_field(name="💰 Precio Pagado", value=f"`{self.mejor_oferta} monedas`", inline=True)
        embed.add_field(name="💳 Tu Nuevo Saldo", value=f"`{nuevo_saldo} monedas`", inline=True)
        if tiene_boost:
            embed.add_field(name="⚡ Boost Aplicado", value=f"+500💰 extra por Boost de Subasta!", inline=False)
        embed.add_field(
            name="📋 Jugador Revelado",
            value=f"{self.jugador_actual['emoji']} **{self.jugador_actual['nombre']}**\n🏆 Posición: `{self.jugador_actual['posicion']}`\n⭐ OVR: `{self.jugador_actual['ovr']}`\n🌍 Nacionalidad: {self.jugador_actual['pais']}",
            inline=False
        )
        embed.set_footer(text="FUTROL — Revisa tu plantilla con /mequipo")
        
        await self.subasta_msg.channel.send(embed=embed)

    @app_commands.command(name="mequipo", description="👕 Ver la plantilla de jugadores que has ganado en la subasta")
    async def mequipo(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_data = db.get_user(user_id)
        equipo = user_data.get("equipo", [])
        saldo = user_data.get("monedas", 1000)

        embed = discord.Embed(
            title=f"👕 Plantilla de {interaction.user.display_name}",
            description=f"Revisa tu colección de cracks fichados en subastas.\n💰 Saldo: `{saldo} monedas`",
            color=0x1F8B4C
        )

        if not equipo:
            embed.add_field(name="🏃 Jugadores en Plantilla", value="Aún no tienes ningún jugador. ¡Participa en la subasta con `/subasta`!", inline=False)
        else:
            lineas = []
            for i, j in enumerate(equipo, 1):
                lineas.append(f"`{i}.` {j['emoji']} **{j['nombre']}** — OVR `{j['ovr']}` ({j['posicion']})")
            
            # Limitar longitud en discord por si el equipo es muy grande
            chunk_size = 10
            for k in range(0, len(lineas), chunk_size):
                chunk = lineas[k:k+chunk_size]
                embed.add_field(name=f"🏃 Jugadores ({k+1} - {min(len(lineas), k+chunk_size)})", value="\n".join(chunk), inline=False)

        embed.set_footer(text="FUTROL — El bot definitivo del fútbol ⚽")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Subasta(bot))