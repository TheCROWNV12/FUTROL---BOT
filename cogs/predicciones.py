import discord
from discord.ext import commands
from discord import app_commands
import random
from utils import db

class Predicciones(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.predicciones = {}
        self._load_preds()

    def _load_preds(self):
        if not self.predicciones:
            self.predicciones = db.get_predicciones_db()

    @app_commands.command(name="predecir", description="🎯 Crear una predicción de partido (solo admins)")
    @app_commands.default_permissions(administrator=True)
    async def predecir(self, interaction: discord.Interaction, equipo_local: str, equipo_visitante: str):
        pid = str(random.randint(1000, 9999))
        data = {
            "local": equipo_local,
            "visitante": equipo_visitante,
            "activa": True,
            "votos": {},
            "resultado_real": None,
            "creador": interaction.user.id,
            "mensaje_id": None,
            "canal_id": interaction.channel_id
        }
        self.predicciones[pid] = data
        db.save_prediccion(pid, data)

        embed = discord.Embed(
            title=f"🎯 PREDICCIÓN ABIERTA — {equipo_local} vs {equipo_visitante}",
            description="Votá tu resultado preferido usando los botones de abajo.\nCuando el partido termine, un admin usará `/cerrar_prediccion`.",
            color=0x3498DB
        )
        embed.add_field(name="🆔 ID", value=f"`{pid}`", inline=True)
        embed.add_field(name="📊 Estado", value="🟢 Abierta", inline=True)
        embed.set_footer(text="FUTROL — Predicciones")

        view = PrediccionVotoView(self, pid)
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_response()
        self.predicciones[pid]["mensaje_id"] = msg.id

    @app_commands.command(name="predicciones_activas", description="📋 Ver todas las predicciones abiertas en el servidor")
    async def predicciones_activas(self, interaction: discord.Interaction):
        activas = {pid: p for pid, p in self.predicciones.items() if p.get("activa", False)}

        if not activas:
            await interaction.response.send_message("📋 No hay predicciones activas en este momento.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📋 PREDICCIONES ACTIVAS",
            color=0x3498DB
        )

        for pid, p in activas.items():
            total = len(p.get("votos", {}))
            embed.add_field(
                name=f"🆔 {pid} — {p['local']} vs {p['visitante']}",
                value=f"📊 Votos: **{total}** participantes",
                inline=False
            )

        embed.set_footer(text="FUTROL — Usá /predecir para crear una nueva")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cerrar_prediccion", description="🔒 Cerrar una predicción y repartir recompensas (solo admins)")
    @app_commands.default_permissions(administrator=True)
    async def cerrar_prediccion(self, interaction: discord.Interaction, id_prediccion: str, resultado: str):
        pid = id_prediccion

        if pid not in self.predicciones:
            preds_db = db.get_predicciones_db()
            if pid in preds_db:
                self.predicciones[pid] = preds_db[pid]
            else:
                await interaction.response.send_message("❌ Esa predicción no existe.", ephemeral=True)
                return

        p = self.predicciones[pid]
        if not p.get("activa", False):
            await interaction.response.send_message("❌ Esa predicción ya está cerrada.", ephemeral=True)
            return

        resultados_validos = ["local", "empate", "visitante"]
        if resultado.lower() not in resultados_validos:
            await interaction.response.send_message(f"❌ Resultado inválido. Usá: `local`, `empate` o `visitante`.", ephemeral=True)
            return

        p["activa"] = False
        p["resultado_real"] = resultado.lower()

        aciertos = 0
        for uid_str, voto in p.get("votos", {}).items():
            if voto == resultado.lower():
                db.add_saldo(int(uid_str), 100)
                aciertos += 1

        resultado_texto = {
            "local": f"🏠 Victoria de {p['local']}",
            "empate": "🤝 Empate",
            "visitante": f"✈️ Victoria de {p['visitante']}"
        }

        embed = discord.Embed(
            title="🔒 PREDICCIÓN CERRADA",
            description=f"**{p['local']} vs {p['visitante']}**\nResultado: **{resultado_texto[resultado.lower()]}**\n\n"
                        f"🎉 **{aciertos}** usuarios acertaron y ganaron **100💰** cada uno!",
            color=0x2ECC71 if aciertos > 0 else 0xE74C3C
        )
        embed.add_field(name="🆔 ID", value=f"`{pid}`", inline=True)

        db.save_prediccion(pid, p)

        await interaction.response.send_message(embed=embed)


class PrediccionVotoView(discord.ui.View):
    def __init__(self, cog, pid):
        super().__init__(timeout=None)
        self.cog = cog
        self.pid = pid

    @discord.ui.button(label="🏠 Local", style=discord.ButtonStyle.success, custom_id="pred_local")
    async def voto_local(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.registrar_voto(interaction, "local")

    @discord.ui.button(label="🤝 Empate", style=discord.ButtonStyle.secondary, custom_id="pred_empate")
    async def voto_empate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.registrar_voto(interaction, "empate")

    @discord.ui.button(label="✈️ Visitante", style=discord.ButtonStyle.danger, custom_id="pred_visit")
    async def voto_visitante(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.registrar_voto(interaction, "visitante")

    async def registrar_voto(self, interaction: discord.Interaction, voto: str):
        pid = self.pid
        p = self.cog.predicciones.get(pid)
        if not p or not p.get("activa", False):
            await interaction.response.send_message("❌ Esta predicción ya está cerrada.", ephemeral=True)
            return

        uid = str(interaction.user.id)
        p["votos"][uid] = voto
        db.save_prediccion(pid, p)

        texto_voto = {"local": "🏠 Local", "empate": "🤝 Empate", "visitante": "✈️ Visitante"}
        await interaction.response.send_message(f"✅ Votaste por **{texto_voto[voto]}** en **{p['local']} vs {p['visitante']}**!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Predicciones(bot))
