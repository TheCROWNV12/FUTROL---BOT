# cogs/reglas.py
import discord
from discord.ext import commands
from discord import app_commands

class Reglas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reglas", description="📜 Ver las reglas de convivencia y juego limpio de FUTROL")
    async def reglas(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 REGLAS DE CONVIVENCIA Y JUEGO LIMPIO — FUTROL",
            description="Para mantener una comunidad competitiva, justa y agradable, todos los mánagers deben cumplir con las siguientes normas:",
            color=0x2C3E50  # Azul Marino
        )
        
        embed.add_field(
            name="1️⃣ Respeto Mutuo",
            value="> Trata a todos los miembros y mánagers con respeto. Queda estrictamente prohibido el lenguaje ofensivo, racista o xenófobo.",
            inline=False
        )
        embed.add_field(
            name="2️⃣ Fair Play (Juego Limpio)",
            value="> Queda prohibido explotar cualquier tipo de bug, error o automatizar comandos de los juegos del bot. Juega limpio.",
            inline=False
        )
        embed.add_field(
            name="3️⃣ Spam de Comandos",
            value="> No inundes los canales públicos con comandos repetitivos. Utiliza los canales específicos designados para jugar con FUTROL.",
            inline=False
        )
        embed.add_field(
            name="4️⃣ Economía del Servidor",
            value="> El dinero virtual es intransferible y no se permite la compra/venta externa de monedas o cuentas. Todo intento será sancionado.",
            inline=False
        )
        
        embed.set_footer(text="FUTROL Bot © — El árbitro siempre tiene la razón ⚽")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ayuda", description="ℹ️ Mostrar el menú de comandos categorizado de FUTROL")
    async def ayuda(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 MANUAL DE COMANDOS — FUTROL",
            description="¡Bienvenido al panel táctico! Aquí tienes todos los comandos disponibles clasificados por categorías:",
            color=0x9B59B6  # Púrpura Elegante
        )
        
        embed.add_field(
            name="🥅 Juegos y Desafíos",
            value=(
                "🔹 `/penal` - Pateá un penal contra el arquero por monedas.\n"
                "🔹 `/trivia` - Responde una pregunta histórica de fútbol (+100💰).\n"
                "🔹 `/impostor` - Crea un lobby para el juego de deducción futbolera."
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔮 Mercado y Colección",
            value=(
                "🔹 `/subasta` - Inicia la subasta interactiva de un crack misterioso.\n"
                "🔹 `/apostar [monedas]` - Haz una puja en la subasta en curso.\n"
                "🔹 `/mequipo` - Revisa las monedas de tu club y tu plantilla de jugadores."
            ),
            inline=False
        )
        
        embed.add_field(
            name="🏆 Gestión del Club (Modo Carrera)",
            value=(
                "🔹 `/carrera` - Revisa tu división, puntos y estadísticas.\n"
                "🔹 `/jugar_partido` - Elige estrategia y simula un partido.\n"
                "🔹 `/entrenar` - Sesión física para ganar monedas y puntos (2h cd).\n"
                "🔹 `/carrera_top` - Tabla de líderes del servidor.\n"
                "🔹 `/historial` - Ver tus últimos partidos.\n"
                "🔹 `/borrar_jugador` - Borrar tu jugador de carrera."
            ),
            inline=False
        )

        embed.add_field(
            name="💰 Economía y Perfil",
            value=(
                "🔹 `/saldo` - Ver monedas, barra de progreso y comparación.\n"
                "🔹 `/perfil` - Perfil completo del mánager.\n"
                "🔹 `/diario` - Recompensa diaria con racha.\n"
                "🔹 `/transferir @user cantidad` - Transferir monedas.\n"
                "🔹 `/tienda` - Comprar mejoras y beneficios.\n"
                "🔹 `/usar_item` - Activar un item de tu inventario.\n"
                "🔹 `/top_ricos` - Ranking de los más ricos."
            ),
            inline=False
        )

        embed.add_field(
            name="🏪 Mercado de Transferencias",
            value=(
                "🔹 `/mercado` - Ver jugadores en venta.\n"
                "🔹 `/vender precio` - Vender un jugador de tu plantilla.\n"
                "🔹 `/comprar id` - Comprar un jugador del mercado."
            ),
            inline=False
        )

        embed.add_field(
            name="⚔️ Duelos y Versus",
            value=(
                "🔹 `/retar @user [apuesta]` - Duelo de penales 1v1.\n"
                "🔹 `/trivia_duelo @user [apuesta]` - Duelo de trivia."
            ),
            inline=False
        )

        embed.add_field(
            name="🎯 Predicciones",
            value=(
                "🔹 `/predecir local visitante` - Crear predicción (admin).\n"
                "🔹 `/predicciones_activas` - Ver predicciones abiertas.\n"
                "🔹 `/cerrar_prediccion id resultado` - Cerrar (admin)."
            ),
            inline=False
        )

        embed.add_field(
            name="🏆 Torneos",
            value=(
                "🔹 `/torneo_crear nombre apuesta` - Crear torneo (admin).\n"
                "🔹 `/torneo_unirse` - Unirse al torneo activo.\n"
                "🔹 `/torneo_iniciar` - Iniciar el torneo (admin)."
            ),
            inline=False
        )

        embed.add_field(
            name="📋 Gestión de Plantilla",
            value=(
                "🔹 `/posiciones` - Ver posiciones de tus jugadores.\n"
                "🔹 `/mequipo` - Ver plantilla de subastas."
            ),
            inline=False
        )

        embed.add_field(
            name="📜 Información General",
            value=(
                "🔹 `/reglas` - Lee las reglas del servidor de FUTROL.\n"
                "🔹 `/info` - Información del bot, versión y creadores.\n"
                "🔹 `/ayuda` - Abre este panel táctico de ayuda."
            ),
            inline=False
        )
        
        embed.set_footer(text="FUTROL — El bot definitivo del fútbol ⚽")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="ℹ️ Información del bot FUTROL")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚽ FUTROL — El Bot Definitivo del Fútbol",
            description="El bot más completo para servidores de fútbol en Discord.\nDesde subastas de cracks hasta modos carrera, trivias épicas y torneos entre miembros.",
            color=0x2ECC71
        )
        embed.add_field(name="🏆 Modos", value="Modo Carrera | 🔮 Subastas | 🧠 Trivia | ⚽ Penales | 🕵️ Impostor | 💰 Economía", inline=False)
        embed.add_field(name="👨‍💻 Creadores", value="**ancestors_kant** & **Exxe**", inline=True)
        embed.add_field(name="🌐 Servidores Activos", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="📌 Versión", value="**10/10** — Mejora Total", inline=False)
        embed.set_footer(text="FUTROL — ¿Necesitás ayuda? Usá /ayuda")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Reglas(bot))