import discord
from discord.ext import commands
from discord import app_commands
import time
import math
from utils import db

DIVISIONES = [
    "D4 — Bronce ⚽",
    "D3 — Plata 🥈",
    "D2 — Oro 🥇",
    "D1 — Élite 👑"
]

def get_division(puntos):
    if puntos < 100:
        return DIVISIONES[0]
    elif puntos < 300:
        return DIVISIONES[1]
    elif puntos < 600:
        return DIVISIONES[2]
    else:
        return DIVISIONES[3]

def barra_progreso(actual, maximo, longitud=10):
    if maximo <= 0:
        return "░" * longitud
    proporcion = actual / maximo
    lleno = min(longitud, math.floor(proporcion * longitud))
    return "▓" * lleno + "░" * (longitud - lleno)

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="saldo", description="💰 Ver tus monedas actuales y estadísticas económicas")
    async def saldo(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        saldo = data.get("monedas", 1000)
        media = db.get_saldo_medio()

        diff = saldo - media
        if diff > 0:
            comparacion = f"📈 **+{diff}** por encima de la media"
        elif diff < 0:
            comparacion = f"📉 **{diff}** por debajo de la media"
        else:
            comparacion = "📊 Estás exactamente en la media"

        barra = barra_progreso(saldo, 5000)
        nivel = "🟢 Alto" if saldo >= 3000 else "🟡 Medio" if saldo >= 1000 else "🔴 Bajo"

        embed = discord.Embed(
            title=f"💰 Saldo de {interaction.user.display_name}",
            color=0xF1C40F
        )
        embed.add_field(name="💳 Monedas", value=f"**{saldo}** 💰", inline=True)
        embed.add_field(name="📊 Nivel", value=nivel, inline=True)
        embed.add_field(name="📈 Comparación", value=comparacion, inline=False)
        embed.add_field(name="📊 Progreso a 5000💰", value=f"{barra} `{saldo}/5000`", inline=False)
        embed.set_footer(text="FUTROL — Usa /diario para tu recompensa diaria")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="perfil", description="👤 Ver tu perfil completo de mánager FUTROL")
    async def perfil(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        saldo = data.get("monedas", 1000)
        puntos = data.get("puntos", 0)
        victorias = data.get("victorias", 0)
        derrotas = data.get("derrotas", 0)
        equipo = data.get("equipo", [])
        insignias = data.get("insignias", [])
        items = data.get("items", [])
        jugador = data.get("jugador")

        div = get_division(puntos)

        embed = discord.Embed(
            title=f"👤 Perfil de {interaction.user.display_name}",
            color=0x9B59B6
        )

        if jugador:
            embed.description = f"👤 **{jugador['nombre']}** {jugador['pais']} — ⭐{jugador['media']} {jugador.get('posicion_nombre', jugador['posicion'])}"

        skin = data.get("skin_estadio")
        if skin:
            embed.add_field(name="🏟️ Estadio", value=skin, inline=False)

        embed.add_field(name="💰 Monedas", value=f"**{saldo}** 💰", inline=True)
        embed.add_field(name="📋 División", value=div, inline=True)
        embed.add_field(name="⭐ Puntos", value=f"`{puntos}` pts", inline=True)
        embed.add_field(name="✅ Victorias", value=f"`{victorias}`", inline=True)
        embed.add_field(name="❌ Derrotas", value=f"`{derrotas}`", inline=True)
        embed.add_field(name="👕 Jugadores", value=f"`{len(equipo)}`", inline=True)

        if insignias:
            lista_insignias = " | ".join(insignias)
            embed.add_field(name="🎖️ Insignias", value=lista_insignias, inline=False)
        else:
            embed.add_field(name="🎖️ Insignias", value="Ninguna aún. ¡Jugá para desbloquear!", inline=False)

        if items:
            items_nombres = []
            for item_id in items:
                for ti in db.ITEMS_TIENDA:
                    if ti["id"] == item_id:
                        items_nombres.append(ti["nombre"])
            embed.add_field(name="🛒 Items", value=", ".join(items_nombres), inline=False)

        embed.set_footer(text="FUTROL — Usa /tienda para comprar mejoras")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="diario", description="📅 Reclamá tu recompensa diaria (renueva cada 24h)")
    async def diario(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        ahora = time.time()
        ultimo = data.get("ultimo_diario", 0.0)
        racha = data.get("diario_racha", 0)

        cooldown = 86400
        tiempo_pasado = ahora - ultimo

        if tiempo_pasado < cooldown:
            restante = cooldown - tiempo_pasado
            horas = int(restante // 3600)
            minutos = int((restante % 3600) // 60)
            await interaction.response.send_message(
                f"⏳ Ya reclamaste tu diario hoy. Volvé en **{horas}h {minutos}m**.",
                ephemeral=True
            )
            return

        if tiempo_pasado >= cooldown * 2:
            racha = 0

        racha += 1
        base = 100
        bonus_racha = min(racha - 1, 6) * 50
        total = base + bonus_racha

        db.add_saldo(user_id, total)
        db.update_user(user_id, ultimo_diario=ahora, diario_racha=racha)

        if racha == 7:
            ok, reward = db.add_insignia(user_id, "racha_diaria_7")
            extra = f" (+{reward}💰)" if reward > 0 else ""
            await interaction.response.send_message(
                f"📅 **¡DIARIO RECLAMADO!**\n\n"
                f"💰 **+{total} monedas**\n"
                f"🔥 Racha: **{racha} días**\n"
                f"🎖️ ¡Desbloqueaste la insignia **Fiel Mánager**!{extra}"
            )
            return

        embed = discord.Embed(
            title="📅 Recompensa Diaria — FUTROL",
            description=f"¡Gracias por volver, {interaction.user.mention}!",
            color=0x2ECC71
        )
        embed.add_field(name="💰 Monedas", value=f"**+{total}**", inline=True)
        embed.add_field(name="🔥 Racha", value=f"**{racha}** días seguidos", inline=True)
        embed.add_field(name="📈 Próximo bonus", value=f"Día {racha+1}: **{base + min(racha, 6) * 50}💰**", inline=False)
        embed.set_footer(text="FUTROL — Volvé mañana para más 💰")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="transferir", description="💸 Transferir monedas a otro mánager")
    async def transferir(self, interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
        user_id = interaction.user.id
        saldo = db.get_saldo(user_id)

        if cantidad <= 0:
            await interaction.response.send_message("❌ La cantidad debe ser positiva.", ephemeral=True)
            return

        if saldo < cantidad:
            await interaction.response.send_message(f"❌ No tenés suficientes monedas. Tenés `{saldo}💰`.", ephemeral=True)
            return

        if usuario.id == user_id:
            await interaction.response.send_message("❌ No podés transferirte a vos mismo.", ephemeral=True)
            return

        db.sub_saldo(user_id, cantidad)
        db.add_saldo(usuario.id, cantidad)

        embed = discord.Embed(
            title="💸 Transferencia Exitosa",
            description=f"{interaction.user.mention} transfirió **{cantidad}💰** a {usuario.mention}",
            color=0x2ECC71
        )
        embed.add_field(name="💰 Tu nuevo saldo", value=f"`{db.get_saldo(user_id)} monedas`", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tienda", description="🛒 Comprá mejoras y beneficios para tu club")
    async def tienda(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        saldo = db.get_saldo(user_id)
        data = db.get_user(user_id)
        items_actuales = data.get("items", [])

        embed = discord.Embed(
            title="🛒 TIENDA FUTROL",
            description=f"💰 Tu saldo: **{saldo} monedas**\nSeleccioná un item abajo para comprarlo.",
            color=0xF1C40F
        )

        for item in db.ITEMS_TIENDA:
            posee = "✅" if item["id"] in items_actuales else ""
            embed.add_field(
                name=f"{item['nombre']} — {item['precio']}💰 {posee}",
                value=item["desc"],
                inline=False
            )

        embed.set_footer(text="FUTROL — Los items se aplican automáticamente al usarlos")
        await interaction.response.send_message(embed=embed, view=TiendaView(user_id, saldo))

    @app_commands.command(name="usar_item", description="🎯 Usar un item de tu inventario")
    @app_commands.choices(item=[
        app_commands.Choice(name="🏋️ Boost de Entreno", value="boost_entreno"),
        app_commands.Choice(name="🏟️ Skin de Estadio", value="skin_estadio"),
        app_commands.Choice(name="🛡️ Protección de Puntos", value="proteccion_puntos"),
        app_commands.Choice(name="⭐ Mejora de Club", value="mejora_club"),
        app_commands.Choice(name="💰 Boost de Subasta", value="boost_subasta")
    ])
    async def usar_item(self, interaction: discord.Interaction, item: app_commands.Choice[str]):
        user_id = interaction.user.id
        item_id = item.value

        if not db.tiene_item(user_id, item_id):
            await interaction.response.send_message(f"❌ No tenés **{item.name}** en tu inventario. Compralo en `/tienda`.", ephemeral=True)
            return

        item_nombres = {
            "boost_entreno": "🏋️ Boost de Entreno",
            "skin_estadio": "🏟️ Skin de Estadio",
            "proteccion_puntos": "🛡️ Protección de Puntos",
            "mejora_club": "⭐ Mejora de Club",
            "boost_subasta": "💰 Boost de Subasta"
        }

        if item_id == "skin_estadio":
            db.update_user(user_id, skin_estadio="🏟️ Estadio Personalizado")
            db.remove_item(user_id, "skin_estadio")
            await interaction.response.send_message("🏟️ ¡Skin de estadio aplicado! Ahora tu estadio tiene un aspecto único.")
        elif item_id == "proteccion_puntos":
            db.update_user(user_id, proteccion_puntos=True)
            db.remove_item(user_id, "proteccion_puntos")
            await interaction.response.send_message("🛡️ ¡Protección activada! No perderás puntos en tu próxima derrota.")
        elif item_id == "mejora_club":
            await interaction.response.send_message("⭐ ¡Mejora de Club activa! Usá `/fichar` para ver clubes globales.")
        elif item_id == "boost_entreno":
            # Apply to next entrenamiento - we mark it
            train_boost = db.get_user(user_id).get("train_boost", 0) + 1
            db.update_user(user_id, train_boost=train_boost)
            db.remove_item(user_id, "boost_entreno")
            await interaction.response.send_message("🏋️ ¡Boost de Entreno activado! Tu próximo entrenamiento dará el doble.")
        elif item_id == "boost_subasta":
            data = db.get_user(user_id)
            if "boost_subasta" in data.get("items", []):
                await interaction.response.send_message("💰 ¡Boost de Subasta listo! Se aplicará automáticamente al ganar una subasta.")
            else:
                await interaction.response.send_message("❌ No tenés este item.")
        else:
            await interaction.response.send_message(f"✅ **{item_nombres.get(item_id, item.name)}** listo para usar.")

    @app_commands.command(name="mercado", description="🏪 Ver el mercado de transferencias de jugadores")
    async def mercado(self, interaction: discord.Interaction):
        db_data = db._read_db()
        mercado_lista = db_data.get("mercado", [])

        embed = discord.Embed(
            title="🏪 MERCADO DE TRANSFERENCIAS",
            description="Jugadores listados por otros mánagers.",
            color=0x9B59B6
        )

        if not mercado_lista:
            embed.description = "No hay jugadores en venta. Usá `/vender` para listar uno."
        else:
            for i, item in enumerate(mercado_lista[:10], 1):
                j = item["jugador"]
                embed.add_field(
                    name=f"{i}. {j['nombre']} ⭐{j['ovr']} — {item['precio']}💰",
                    value=f"Vendedor: <@{item['vendedor']}> | `ID: {item['id']}`",
                    inline=False
                )

        embed.set_footer(text="Usá /vender o /comprar para operar")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vender", description="💰 Vender un jugador de tu plantilla en el mercado")
    async def vender(self, interaction: discord.Interaction, precio: int):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        equipo = data.get("equipo", [])

        if not equipo:
            await interaction.response.send_message("❌ No tenés jugadores para vender.", ephemeral=True)
            return

        if precio <= 0 or precio > 100000:
            await interaction.response.send_message("❌ Precio inválido (1-100000).", ephemeral=True)
            return

        embed = discord.Embed(
            title="💰 VENDER JUGADOR",
            description="Seleccioná qué jugador querés vender:",
            color=0xF1C40F
        )
        for i, j in enumerate(equipo[:25], 1):
            embed.add_field(name=f"{i}. {j['nombre']} ⭐{j['ovr']}", value=f"{j['posicion']} — {j['pais']}", inline=True)

        embed.set_footer(text="Respondé con el número del jugador a vender (10s)")
        await interaction.response.send_message(embed=embed)

        def check(m):
            return m.author.id == user_id and m.channel.id == interaction.channel_id and m.content.isdigit()

        try:
            msg = await self.bot.wait_for("message", timeout=10.0, check=check)
            idx = int(msg.content) - 1
            if idx < 0 or idx >= len(equipo):
                await interaction.followup.send("❌ Número inválido.")
                return
        except:
            await interaction.followup.send("⏰ Tiempo agotado.")
            return

        jugador = equipo.pop(idx)
        db.update_user(user_id, equipo=equipo)

        db_data = db._read_db()
        mercado_lista = db_data.get("mercado", [])
        venta_id = str(random.randint(10000, 99999))
        mercado_lista.append({
            "id": venta_id,
            "vendedor": user_id,
            "jugador": jugador,
            "precio": precio
        })
        db_data["mercado"] = mercado_lista
        db._write_db(db_data)

        await interaction.followup.send(f"💰 Listaste a **{jugador['nombre']}** ⭐{jugador['ovr']} por **{precio}💰** (ID: `{venta_id}`).")

    @app_commands.command(name="comprar", description="💵 Comprar un jugador del mercado de transferencias")
    async def comprar(self, interaction: discord.Interaction, id_venta: str):
        comprador_id = interaction.user.id
        db_data = db._read_db()
        mercado_lista = db_data.get("mercado", [])

        venta = None
        for v in mercado_lista:
            if v["id"] == id_venta:
                venta = v
                break

        if not venta:
            await interaction.response.send_message("❌ Esa venta no existe o ya fue comprada.", ephemeral=True)
            return

        if venta["vendedor"] == comprador_id:
            await interaction.response.send_message("❌ No podés comprar tu propio jugador.", ephemeral=True)
            return

        saldo = db.get_saldo(comprador_id)
        if saldo < venta["precio"]:
            await interaction.response.send_message(f"❌ No tenés suficientes monedas. Necesitás `{venta['precio']}💰`.", ephemeral=True)
            return

        db.sub_saldo(comprador_id, venta["precio"])
        db.add_saldo(venta["vendedor"], venta["precio"])
        db.add_jugador(comprador_id, venta["jugador"])

        mercado_lista.remove(venta)
        db_data["mercado"] = mercado_lista
        db._write_db(db_data)

        j = venta["jugador"]
        embed = discord.Embed(
            title="💵 ¡TRANSFERENCIA COMPLETADA!",
            description=f"{interaction.user.mention} compró **{j['nombre']}** ⭐{j['ovr']} por **{venta['precio']}💰**",
            color=0x2ECC71
        )
        embed.add_field(name="💰 Tu nuevo saldo", value=f"`{db.get_saldo(comprador_id)} monedas`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="top_ricos", description="👑 Ranking de los usuarios con más monedas del servidor")
    async def top_ricos(self, interaction: discord.Interaction):
        leaderboard = db.get_leaderboard_rico(limit=10)
        media = db.get_saldo_medio()

        embed = discord.Embed(
            title="👑 TOP RICOS — FUTROL",
            description=f"Los mánagers con más monedas del servidor.\n📊 Media del servidor: **{media}💰**",
            color=0xFFD700
        )

        if not leaderboard:
            embed.description = "Aún no hay mánagers registrados."
        else:
            texto = ""
            for i, entry in enumerate(leaderboard, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"`{i}.`"
                user = self.bot.get_user(int(entry["id"]))
                nombre = user.display_name if user else f"ID: {entry['id']}"
                texto += f"{emoji} **{nombre}** — `{entry['monedas']}💰`\n"
            embed.description = texto

        embed.set_footer(text="FUTROL — Usá /diario para ganar monedas todos los días")
        await interaction.response.send_message(embed=embed)


class TiendaView(discord.ui.View):
    def __init__(self, user_id, saldo):
        super().__init__(timeout=60)
        self.user_id = user_id

        for item in db.ITEMS_TIENDA:
            btn = TiendaButton(item, user_id, saldo)
            self.add_item(btn)


class TiendaButton(discord.ui.Button):
    def __init__(self, item, user_id, saldo):
        self.item = item
        self.user_id = user_id
        data = db.get_user(user_id)
        items_actuales = data.get("items", [])
        puede_comprar = saldo >= item["precio"] and item["id"] not in items_actuales
        super().__init__(
            label=f"{item['nombre']} ({item['precio']}💰)",
            style=discord.ButtonStyle.success if puede_comprar else discord.ButtonStyle.secondary,
            disabled=not puede_comprar,
            custom_id=f"buy_{item['id']}"
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta tienda no es tuya.", ephemeral=True)
            return

        saldo = db.get_saldo(self.user_id)
        if saldo < self.item["precio"]:
            await interaction.response.send_message(f"❌ No tenés suficientes monedas. Necesitás `{self.item['precio']}💰`.", ephemeral=True)
            return

        data = db.get_user(self.user_id)
        if self.item["id"] in data.get("items", []):
            await interaction.response.send_message("❌ Ya tenés este item.", ephemeral=True)
            return

        db.sub_saldo(self.user_id, self.item["precio"])
        db.add_item(self.user_id, self.item["id"])

        embed = discord.Embed(
            title="✅ ¡Compra Exitosa!",
            description=f"Adquiriste **{self.item['nombre']}** por **{self.item['precio']}💰**",
            color=0x2ECC71
        )
        embed.add_field(name="📖 Descripción", value=self.item["desc"], inline=False)
        embed.add_field(name="💰 Saldo restante", value=f"`{db.get_saldo(self.user_id)} monedas`", inline=False)

        await interaction.response.send_message(embed=embed)


class MercadoView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.select(
        placeholder="Elegí un jugador para vender...",
        custom_id="vender_select"
    )
    async def vender_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ No podés interactuar con esto.", ephemeral=True)
            return
        await interaction.response.send_message("Usá `/vender numero_precio` para listar tu jugador en el mercado.", ephemeral=True)

    @discord.ui.select(
        placeholder="Elegí un jugador del mercado para comprar...",
        custom_id="comprar_select"
    )
    async def comprar_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ No podés interactuar con esto.", ephemeral=True)
            return
        await interaction.response.send_message("Usá `/comprar id_jugador` para comprar del mercado.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Economia(bot))
