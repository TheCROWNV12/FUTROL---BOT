import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from utils import db

class Torneos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.torneo_activo = None

    @app_commands.command(name="torneo_crear", description="🏆 Crear un torneo entre miembros del servidor")
    @app_commands.default_permissions(administrator=True)
    async def torneo_crear(self, interaction: discord.Interaction, nombre: str, apuesta: int = 100):
        if self.torneo_activo:
            await interaction.response.send_message("❌ Ya hay un torneo activo. Terminálo antes de crear otro.", ephemeral=True)
            return

        self.torneo_activo = {
            "nombre": nombre,
            "apuesta": max(1, apuesta),
            "participantes": [],
            "inscriptos": {},
            "brackets": [],
            "etapa": "inscripcion",
            "creador": interaction.user.id,
            "canal_id": interaction.channel_id
        }

        embed = discord.Embed(
            title=f"🏆 {nombre} — TORNEO CREADO",
            description=f"💰 Apuesta por participante: **{apuesta} monedas**\n\nUsá `/torneo_unirse` para participar.\nUsá `/torneo_iniciar` cuando haya suficientes jugadores.",
            color=0xFFD700
        )
        embed.set_footer(text="Mínimo 2 participantes para iniciar")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="torneo_unirse", description="🏆 Unirte al torneo activo")
    async def torneo_unirse(self, interaction: discord.Interaction):
        if not self.torneo_activo:
            await interaction.response.send_message("❌ No hay un torneo activo en este momento.", ephemeral=True)
            return

        t = self.torneo_activo
        if t["etapa"] != "inscripcion":
            await interaction.response.send_message("❌ Las inscripciones ya están cerradas.", ephemeral=True)
            return

        uid = interaction.user.id
        if uid in [p["id"] for p in t["participantes"]]:
            await interaction.response.send_message("❌ Ya estás inscrito en el torneo.", ephemeral=True)
            return

        saldo = db.get_saldo(uid)
        if saldo < t["apuesta"]:
            await interaction.response.send_message(f"❌ No tenés suficientes monedas. Necesitás `{t['apuesta']}💰`.", ephemeral=True)
            return

        db.sub_saldo(uid, t["apuesta"])
        t["participantes"].append({
            "id": uid,
            "nombre": interaction.user.display_name,
            "activo": True
        })

        embed = discord.Embed(
            title=f"✅ ¡INSCRIPTO!",
            description=f"{interaction.user.mention} se unió a **{t['nombre']}**\n💰 Apuesta pagada: **{t['apuesta']} monedas**",
            color=0x2ECC71
        )
        embed.add_field(name="👥 Participantes", value=f"**{len(t['participantes'])}** mánagers", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="torneo_iniciar", description="🏆 Iniciar el torneo con los participantes actuales")
    @app_commands.default_permissions(administrator=True)
    async def torneo_iniciar(self, interaction: discord.Interaction):
        if not self.torneo_activo:
            await interaction.response.send_message("❌ No hay un torneo activo.", ephemeral=True)
            return

        t = self.torneo_activo
        if t["etapa"] != "inscripcion":
            await interaction.response.send_message("❌ El torneo ya comenzó.", ephemeral=True)
            return

        if len(t["participantes"]) < 2:
            await interaction.response.send_message("❌ Se necesitan al menos 2 participantes.", ephemeral=True)
            return

        t["etapa"] = "en_curso"
        participantes = list(t["participantes"])
        random.shuffle(participantes)

        if len(participantes) % 2 != 0:
            participantes.pop()

        t["brackets"] = []
        for i in range(0, len(participantes), 2):
            t["brackets"].append({
                "p1": participantes[i],
                "p2": participantes[i+1],
                "ganador": None
            })

        embed = discord.Embed(
            title=f"🏆 {t['nombre']} — ¡COMIENZA EL TORNEO!",
            description=f"**{len(participantes)}** mánagers compiten por la gloria.\n💰 Pool total: **{len(t['participantes']) * t['apuesta']} monedas**",
            color=0xFFD700
        )

        for i, bracket in enumerate(t["brackets"], 1):
            embed.add_field(
                name=f"⚔️ Enfrentamiento {i}",
                value=f"{bracket['p1']['nombre']} vs {bracket['p2']['nombre']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)
        await self.simular_torneo(interaction)

    async def simular_torneo(self, interaction):
        t = self.torneo_activo
        canal = interaction.channel

        ronda = 1
        while t["brackets"] and t["etapa"] == "en_curso":
            await asyncio.sleep(2)

            embed_r = discord.Embed(
                title=f"🏆 {t['nombre']} — RONDA {ronda}",
                color=0xE67E22
            )

            siguientes = []
            for bracket in t["brackets"]:
                p1 = bracket["p1"]
                p2 = bracket["p2"]
                ganador = random.choice([p1, p2])
                bracket["ganador"] = ganador
                siguientes.append(ganador)

                perdedor = p1 if ganador["id"] == p2["id"] else p2
                embed_r.add_field(
                    name=f"⚔️ {p1['nombre']} vs {p2['nombre']}",
                    value=f"🏆 **{ganador['nombre']}** avanza! (❌ {perdedor['nombre']} eliminado)",
                    inline=False
                )

            await canal.send(embed=embed_r)
            ronda += 1

            if len(siguientes) == 1:
                campeon = siguientes[0]
                t["etapa"] = "finalizado"
                premio = len(t["participantes"]) * t["apuesta"]
                db.add_saldo(campeon["id"], premio)

                embed_f = discord.Embed(
                    title=f"🏆 ¡{t['nombre']} — CAMPEÓN!",
                    description=f"👑 **{campeon['nombre']}** es el campeón del torneo!\n"
                                f"💰 Premio: **{premio} monedas**",
                    color=0xFFD700
                )
                await canal.send(embed=embed_f)
                self.torneo_activo = None
                return

            t["brackets"] = []
            random.shuffle(siguientes)
            if len(siguientes) % 2 != 0:
                await canal.send(f"🔄 **{siguientes[-1]['nombre']}** pasa a la siguiente ronda directo por sorteo.")
                siguientes.pop()

            for i in range(0, len(siguientes), 2):
                t["brackets"].append({
                    "p1": siguientes[i],
                    "p2": siguientes[i+1],
                    "ganador": None
                })


async def setup(bot):
    await bot.add_cog(Torneos(bot))
