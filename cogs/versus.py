import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from utils import db


class DueloPenalView(discord.ui.View):
    def __init__(self, retador, oponente, apuesta):
        super().__init__(timeout=30)
        self.retador = retador
        self.oponente = oponente
        self.apuesta = apuesta
        self.lados = {}

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        self.stop()

    @discord.ui.select(
        placeholder="Elegí tu lado...",
        options=[
            discord.SelectOption(label="Izquierda ⬅️", value="izquierda"),
            discord.SelectOption(label="Centro ⬆️", value="centro"),
            discord.SelectOption(label="Derecha ➡️", value="derecha"),
        ]
    )
    async def lado_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id not in (self.retador.id, self.oponente.id):
            await interaction.response.send_message("❌ No participás en este duelo.", ephemeral=True)
            return

        uid = interaction.user.id
        if uid in self.lados:
            await interaction.response.send_message("⚠️ Ya elegiste tu lado.", ephemeral=True)
            return

        self.lados[uid] = select.values[0]
        await interaction.response.send_message(f"✅ Elegiste tu lado en secreto. Esperando al otro jugador...", ephemeral=True)

        if len(self.lados) == 2:
            self.stop()

    @discord.ui.button(label="Cancelar 🚫", style=discord.ButtonStyle.danger, custom_id="cancel_duelo")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.retador.id:
            await interaction.response.send_message("❌ Solo el retador puede cancelar.", ephemeral=True)
            return
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="🚫 Duelo cancelado.", embed=None, view=self)
        self.stop()


class TriviaDueloPregunta(discord.ui.View):
    def __init__(self, opciones, duelo_ref, pregunta_idx):
        super().__init__(timeout=18)
        self.duelo_ref = duelo_ref
        self.pregunta_idx = pregunta_idx
        self.opciones = opciones
        self.respondido = False

        letras = ["🇦", "🇧", "🇨", "🇩"]
        for i, op in enumerate(opciones):
            btn = discord.ui.Button(label=f"{letras[i]} {op[:80]}", style=discord.ButtonStyle.primary, custom_id=f"td_{pregunta_idx}_{i}")
            btn.callback = lambda interaction, idx=i: self.handle_answer(interaction, idx)
            self.add_item(btn)

    async def handle_answer(self, interaction: discord.Interaction, idx: int):
        if self.respondido:
            await interaction.response.send_message("⏳ Ya alguien respondió esta pregunta.", ephemeral=True)
            return

        uid = interaction.user.id
        if uid not in (self.duelo_ref.p1.id, self.duelo_ref.p2.id):
            await interaction.response.send_message("❌ No participás en este duelo.", ephemeral=True)
            return

        self.respondido = True
        for child in self.children:
            child.disabled = True

        pq = self.duelo_ref.preguntas[self.pregunta_idx]
        opciones = pq["opciones"]
        correcta = pq["r"]
        elegida = opciones[idx]
        acierto = elegida == correcta

        if uid == self.duelo_ref.p1.id:
            if acierto:
                self.duelo_ref.p1_pts += 1
        else:
            if acierto:
                self.duelo_ref.p2_pts += 1

        await interaction.response.edit_message(view=self)

        msg = "✅ ¡Respuesta correcta!" if acierto else "❌ Respuesta incorrecta."
        await interaction.followup.send(f"{interaction.user.mention} {msg}", ephemeral=False)


class Versus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="retar", description="⚔️ Retá a un duelo de penales 1v1 a otro mánager")
    async def retar(self, interaction: discord.Interaction, usuario: discord.Member, apuesta: int = 50):
        if usuario.id == interaction.user.id:
            await interaction.response.send_message("❌ No podés retarte a vos mismo.", ephemeral=True)
            return

        if apuesta <= 0:
            await interaction.response.send_message("❌ La apuesta debe ser positiva.", ephemeral=True)
            return

        saldo_retador = db.get_saldo(interaction.user.id)
        saldo_oponente = db.get_saldo(usuario.id)

        if saldo_retador < apuesta:
            await interaction.response.send_message(f"❌ No tenés suficientes monedas. Tenés `{saldo_retador}💰`.", ephemeral=True)
            return

        if saldo_oponente < apuesta:
            await interaction.response.send_message(f"❌ {usuario.mention} no tiene suficientes monedas (`{saldo_oponente}💰`).", ephemeral=True)
            return

        embed = discord.Embed(
            title="⚔️ DUELO DE PENALES — FUTROL",
            description=f"{interaction.user.mention} retó a {usuario.mention} a un duelo de penales!\n\n"
                        f"💰 Apuesta: **{apuesta} monedas**\n"
                        f"Cada uno elige su lado en secreto. ¡Que gane el mejor!",
            color=0xE74C3C
        )
        embed.set_footer(text="Usá el menú desplegable para elegir tu lado")

        view = DueloPenalView(interaction.user, usuario, apuesta)
        await interaction.response.send_message(content=f"{interaction.user.mention} vs {usuario.mention}", embed=embed, view=view)
        msg = await interaction.original_response()

        await asyncio.sleep(1)
        await view.wait()

        for child in view.children:
            child.disabled = True

        if len(view.lados) < 2:
            embed_t = discord.Embed(
                title="⏰ TIEMPO AGOTADO",
                description="No se completaron las elecciones a tiempo.",
                color=0x95A5A6
            )
            await msg.edit(embed=embed_t, view=view)
            return

        lado1 = view.lados[interaction.user.id]
        lado2 = view.lados[usuario.id]

        acierto1 = random.choice(["izquierda", "centro", "derecha"]) != lado1
        acierto2 = random.choice(["izquierda", "centro", "derecha"]) != lado2

        if acierto1 and not acierto2:
            ganador = interaction.user
            perdedor = usuario
        elif acierto2 and not acierto1:
            ganador = usuario
            perdedor = interaction.user
        else:
            embed_e = discord.Embed(
                title="🤝 EMPATE",
                description="Ambos anotaron (o ambos fallaron). Nadie pierde monedas.",
                color=0xF1C40F
            )
            await msg.edit(embed=embed_e, view=view)
            return

        db.sub_saldo(perdedor.id, apuesta)
        db.add_saldo(ganador.id, apuesta)

        embed_r = discord.Embed(
            title="⚔️ RESULTADO DEL DUELO",
            description=f"🏆 **{ganador.mention}** ganó el duelo y se lleva **{apuesta}💰** de {perdedor.mention}!",
            color=0x2ECC71
        )
        embed_r.add_field(name="🎯 Tiros", value=f"{interaction.user.display_name}: {'✅' if acierto1 else '❌'}\n{usuario.display_name}: {'✅' if acierto2 else '❌'}", inline=False)
        await msg.edit(embed=embed_r, view=view)

    @app_commands.command(name="trivia_duelo", description="🧠 Duelo de trivia: 5 preguntas, el primero en responder gana")
    async def trivia_duelo(self, interaction: discord.Interaction, usuario: discord.Member, apuesta: int = 50):
        if usuario.id == interaction.user.id:
            await interaction.response.send_message("❌ No podés retarte a vos mismo.", ephemeral=True)
            return

        if apuesta <= 0:
            await interaction.response.send_message("❌ La apuesta debe ser positiva.", ephemeral=True)
            return

        saldo_r = db.get_saldo(interaction.user.id)
        saldo_o = db.get_saldo(usuario.id)
        if saldo_r < apuesta or saldo_o < apuesta:
            await interaction.response.send_message("❌ Alguien no tiene suficientes monedas.", ephemeral=True)
            return

        from cogs.trivia import PREGUNTAS
        preguntas = random.sample(PREGUNTAS, min(5, len(PREGUNTAS)))

        self.p1 = interaction.user
        self.p2 = usuario
        self.preguntas = preguntas
        self.p1_pts = 0
        self.p2_pts = 0
        self.apuesta = apuesta

        embed = discord.Embed(
            title="🧠 TRIVIA DUELO — FUTROL",
            description=f"{interaction.user.mention} vs {usuario.mention}\n💰 Apuesta: **{apuesta} monedas**\n\nPrimero en responder correctamente gana el punto.",
            color=0x9B59B6
        )
        embed.set_footer(text="Pregunta 1/5")
        await interaction.response.send_message(embed=embed)

        for i, pq in enumerate(preguntas):
            opciones = list(pq["opciones"])
            random.shuffle(opciones)

            e_p = discord.Embed(
                title=f"🧠 Pregunta {i+1}/5",
                description=f"**{pq['p']}**",
                color=0x3498DB
            )
            letras = ["🇦", "🇧", "🇨", "🇩"]
            texto_op = "\n".join([f"{letras[j]} {opciones[j]}" for j in range(len(opciones))])
            e_p.add_field(name="Opciones", value=texto_op, inline=False)
            e_p.add_field(name="📊 Marcador", value=f"{interaction.user.display_name}: **{self.p1_pts}** | {usuario.display_name}: **{self.p2_pts}**", inline=False)

            view = TriviaDueloPregunta(opciones, self, i)
            await interaction.followup.send(embed=e_p, view=view)

            await asyncio.sleep(18)

        if self.p1_pts > self.p2_pts:
            ganador = interaction.user
            perdedor = usuario
        elif self.p2_pts > self.p1_pts:
            ganador = usuario
            perdedor = interaction.user
        else:
            embed_f = discord.Embed(
                title="🤝 TRIVIA DUELO — EMPATE",
                description=f"Empate **{self.p1_pts}-{self.p2_pts}**. Nadie pierde monedas.",
                color=0xF1C40F
            )
            await interaction.followup.send(embed=embed_f)
            return

        db.sub_saldo(perdedor.id, apuesta)
        db.add_saldo(ganador.id, apuesta)

        embed_f = discord.Embed(
            title="🏆 TRIVIA DUELO — FINAL",
            description=f"🏆 **{ganador.mention}** ganó el duelo **{self.p1_pts}-{self.p2_pts}** y se lleva **{apuesta}💰**!",
            color=0x2ECC71
        )
        await interaction.followup.send(embed=embed_f)


async def setup(bot):
    await bot.add_cog(Versus(bot))
