# cogs/penales.py
import discord
from discord.ext import commands
from discord import app_commands
import random
from utils import db

class PenalButtons(discord.ui.View):
    def __init__(self, author, cost, reward, racha=0):
        super().__init__(timeout=20)
        self.author = author
        self.cost = cost
        self.reward = reward
        self.racha = racha

    async def on_timeout(self):
        # Deshabilitar botones si se agota el tiempo
        for child in self.children:
            child.disabled = True
        # Nota: En un timeout no tenemos la interacción inicial,
        # así que la deshabilitación se reflejará si se edita el mensaje más tarde,
        # pero es buena práctica parar la vista.
        self.stop()

    async def process_shot(self, interaction: discord.Interaction, lado_elegido):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ ¡Este penal no es tuyo!", ephemeral=True)
            return

        # Deshabilitar todos los botones
        for child in self.children:
            child.disabled = True
        
        await interaction.response.defer()

        user_id = self.author.id
        data = db.get_user(user_id)
        racha = data.get("racha_penales", 0)

        # Determinar tiro y resultado
        arco = random.choice(["izquierda", "centro", "derecha"])
        gol = lado_elegido != arco

        if gol:
            # Streak bonus: cada 3 seguidos, premio doble
            nueva_racha = racha + 1
            bonus = 2 if nueva_racha % 3 == 0 and nueva_racha > 0 else 1
            recompensa_final = self.reward * bonus
            db.update_user(user_id, racha_penales=nueva_racha)
            db.add_saldo(user_id, recompensa_final)
            racha_texto = f"\n🔥 Racha: **{nueva_racha}** penales seguidos"
            if bonus > 1:
                racha_texto += f"\n⚡ ¡RACHA x{bonus}! Premio duplicado: **+{recompensa_final}💰**"
            resultado = f"⚽ **¡GOOOOOL! 🎉**\n¡Excesiva definición! Ganaste **{recompensa_final} monedas** 💰{racha_texto}"
            color = 0x2ECC71
        else:
            db.update_user(user_id, racha_penales=0)
            db.sub_saldo(user_id, self.cost)
            resultado = f"🧤 **¡ATAJADO! 🧤**\nEl arquero adivinó tu intención. Perdiste **{self.cost} monedas** 💔\n🔥 Racha de penales reiniciada."
            color = 0xE74C3C

        nuevo_saldo = db.get_saldo(user_id)

        embed = discord.Embed(
            title="⚽ RESULTADO DEL PENAL",
            description=resultado,
            color=color
        )
        embed.add_field(name="👤 Tu disparo", value=f"`{lado_elegido.upper()}`", inline=True)
        embed.add_field(name="🧤 El arquero fue a", value=f"`{arco.upper()}`", inline=True)
        embed.add_field(name="💰 Saldo actual", value=f"{nuevo_saldo} monedas", inline=False)
        embed.set_footer(text="FUTROL — ¿Volvemos a patear? /penal ⚽")

        await interaction.edit_original_response(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="Izquierda ⬅️", style=discord.ButtonStyle.primary, custom_id="penal_izq")
    async def izq(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_shot(interaction, "izquierda")

    @discord.ui.button(label="Centro ⬆️", style=discord.ButtonStyle.primary, custom_id="penal_cen")
    async def cen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_shot(interaction, "centro")

    @discord.ui.button(label="Derecha ➡️", style=discord.ButtonStyle.primary, custom_id="penal_der")
    async def der(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_shot(interaction, "derecha")


class Penales(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="penal", description="🥅 Pateá un penal contra el arquero por monedas")
    async def penal(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        saldo = db.get_saldo(user_id)
        data = db.get_user(user_id)
        racha = data.get("racha_penales", 0)

        cost = 30
        reward = 50

        # Si el usuario no tiene suficiente dinero
        if saldo < cost:
            # Opción amigable: el club le patrocina el penal pero con menor premio
            cost = 0
            reward = 15
            patrocinado = True
        else:
            patrocinado = False

        embed = discord.Embed(
            title="🥅 ¡TIRO DE PENAL — FUTROL!",
            description="El estadio ruge. El arquero se posiciona bajo los tres palos...\n¿A qué lado vas a disparar?",
            color=0x3498DB
        )
        if racha > 0:
            embed.add_field(name="🔥 Racha Actual", value=f"Llevás **{racha}** penales consecutivos anotados.\n¡Cada **3** seguidos el premio se duplica!", inline=False)
        if patrocinado:
            embed.add_field(name="⚠️ Patrocinio del Club", value="No tienes suficientes monedas para la apuesta de 30💰.\nEl club te patrocina este penal: **Costo 0💰 | Recompensa 15💰**.", inline=False)
        else:
            embed.add_field(name="💵 Apuesta", value=f"Costo: **{cost} monedas** 💰\nSi anotas: **+{reward} monedas** 🏆", inline=False)
            
        embed.set_footer(text="Tienes 20 segundos para patear • FUTROL")

        view = PenalButtons(interaction.user, cost, reward, racha)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Penales(bot))