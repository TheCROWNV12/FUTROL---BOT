# cogs/impostor.py
import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class LobbyView(discord.ui.View):
    def __init__(self, host):
        super().__init__(timeout=120)  # Lobby expira en 2 minutos si no se inicia
        self.host = host
        self.players = [host]  # El host se une automáticamente

    async def update_lobby_message(self, interaction: discord.Interaction):
        # Generar lista de jugadores formateada
        player_list = "\n".join([f"• {p.mention}" for p in self.players])
        
        embed = discord.Embed(
            title="🕵️ LOBBY: MODO IMPOSTOR — FUTROL",
            description="¡El juego de deducción del fútbol! ¿Quién es el impostor que falla los pases a propósito?\n\nPresiona **Unirse** para registrarte. El anfitrión puede iniciar la partida.",
            color=0x8B0000
        )
        embed.add_field(name="👑 Anfitrión", value=self.host.mention, inline=True)
        embed.add_field(name="👥 Jugadores Registrados", value=player_list or "Nadie", inline=False)
        embed.add_field(name="📈 Estado", value=f"Esperando jugadores... ({len(self.players)} registrados. Mínimo 3)", inline=False)
        embed.set_footer(text="Lobby expira en 120s • FUTROL")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Unirse / Salir 👥", style=discord.ButtonStyle.success, custom_id="lobby_join")
    async def join_leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            if interaction.user == self.host:
                await interaction.response.send_message("❌ Eres el anfitrión, no puedes abandonar el lobby. Puedes cancelar la partida dejando expirar el tiempo.", ephemeral=True)
                return
            self.players.remove(interaction.user)
        else:
            self.players.append(interaction.user)
        
        await self.update_lobby_message(interaction)

    @discord.ui.button(label="Iniciar Partida 🎮", style=discord.ButtonStyle.danger, custom_id="lobby_start")
    async def start_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host.id:
            await interaction.response.send_message("❌ Solo el anfitrión puede iniciar la partida.", ephemeral=True)
            return

        if len(self.players) < 3:
            await interaction.response.send_message("⚠️ Se necesitan al menos 3 jugadores en el lobby para iniciar.", ephemeral=True)
            return

        # Deshabilitar botones para que no se pulse más
        for child in self.children:
            child.disabled = True
        
        await interaction.response.defer()

        # Determinar impostores
        num_players = len(self.players)
        num_impostors = max(1, num_players // 5)  # 20% aprox, mínimo 1
        
        shuffled = list(self.players)
        random.shuffle(shuffled)
        
        impostors = shuffled[:num_impostors]
        
        # Editar el mensaje del lobby
        embed = discord.Embed(
            title="🎮 ¡PARTIDA DE IMPOSTOR INICIADA!",
            description="Los roles han sido enviados por Mensaje Directo (DM).\n¡Revisa tu chat privado!",
            color=0x27AE60
        )
        embed.add_field(name="👥 Total Jugadores", value=str(num_players), inline=True)
        embed.add_field(name="🔴 Cantidad de Impostores", value=str(num_impostors), inline=True)
        
        player_mentions = ", ".join([p.mention for p in self.players])
        embed.add_field(name="🏃 Elenco", value=player_mentions, inline=False)
        embed.set_footer(text="FUTROL — El impostor camina entre nosotros...")
        
        await interaction.edit_original_response(embed=embed, view=self)
        
        # Enviar DMs a los jugadores
        for p in self.players:
            es_impostor = p in impostors
            rol_text = (
                "🔴 **IMPOSTOR**\n"
                "Tu objetivo es sabotear los pases y las jugadas sin que te descubran. "
                "Disimula y culpa a otros."
            ) if es_impostor else (
                "🟢 **JUGADOR LEAL**\n"
                "Tu objetivo es cooperar, pasar bien el balón y descubrir quién es el impostor "
                "basándote en sus actitudes sospechosas."
            )
            
            dm_embed = discord.Embed(
                title="🕵️ ROL ASIGNADO — FUTROL IMPOSTOR",
                description=rol_text,
                color=0x8B0000 if es_impostor else 0x27AE60
            )
            dm_embed.set_footer(text="No reveles esta información a nadie.")
            
            try:
                await p.send(embed=dm_embed)
            except discord.Forbidden:
                await interaction.channel.send(f"⚠️ {p.mention}, ¡tienes los DMs cerrados! No pude enviarte tu rol. Abre tus mensajes privados para la próxima.")
        
        self.stop()

    async def on_timeout(self):
        # Deshabilitar botones al expirar
        for child in self.children:
            child.disabled = True
        self.stop()

class Impostor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="impostor", description="🕵️ Iniciar juego del impostor futbolero en el servidor")
    async def impostor(self, interaction: discord.Interaction):
        # Crear lobby
        embed = discord.Embed(
            title="🕵️ LOBBY: MODO IMPOSTOR — FUTROL",
            description="¡El juego de deducción del fútbol! ¿Quién es el impostor que falla los pases a propósito?\n\nPresiona **Unirse** para registrarte. El anfitrión puede iniciar la partida.",
            color=0x8B0000
        )
        embed.add_field(name="👑 Anfitrión", value=interaction.user.mention, inline=True)
        embed.add_field(name="👥 Jugadores Registrados", value=f"• {interaction.user.mention}", inline=False)
        embed.add_field(name="📈 Estado", value="Esperando jugadores... (1 registrado. Mínimo 3)", inline=False)
        embed.set_footer(text="Lobby expira en 120s • FUTROL")

        view = LobbyView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Impostor(bot))