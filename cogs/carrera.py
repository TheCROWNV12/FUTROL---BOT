import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import time
import math
from utils import db


def barra_progreso(actual, maximo, longitud=10):
    if maximo <= 0:
        return "░" * longitud
    proporcion = actual / maximo
    lleno = min(longitud, math.floor(proporcion * longitud))
    return "▓" * lleno + "░" * (longitud - lleno)

DIVISIONES = [
    "D4 — Bronce ⚽",
    "D3 — Plata 🥈",
    "D2 — Oro 🥇",
    "D1 — Élite 👑"
]

OPONENTES = [
    "Real Madrid 🇪🇸", "FC Barcelona 🇪🇸", "Manchester City 🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Bayern Múnich 🇩🇪", "Paris Saint-Germain 🇫🇷", "Liverpool FC 🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Juventus 🇮🇹", "Boca Juniors 🇦🇷", "River Plate 🇦🇷", "Flamengo 🇧🇷",
    "Chelsea 🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Inter Milan 🇮🇹", "AC Milan 🇮🇹", "Ajax 🇳🇱",
    "Benfica 🇵🇹", "Porto 🇵🇹", "Sporting CP 🇵🇹", "PSV 🇳🇱"
]

PAISES = {
    "Argentina": "🇦🇷", "Brasil": "🇧🇷", "Chile": "🇨🇱", "Colombia": "🇨🇴",
    "Ecuador": "🇪🇨", "Perú": "🇵🇪", "Uruguay": "🇺🇾", "Paraguay": "🇵🇾",
    "Bolivia": "🇧🇴", "Venezuela": "🇻🇪", "México": "🇲🇽", "España": "🇪🇸",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Italia": "🇮🇹", "Alemania": "🇩🇪",
    "Francia": "🇫🇷", "Portugal": "🇵🇹", "Países Bajos": "🇳🇱",
    "Estados Unidos": "🇺🇸", "Canadá": "🇨🇦", "Japón": "🇯🇵",
    "Corea del Sur": "🇰🇷", "Nigeria": "🇳🇬", "Costa de Marfil": "🇨🇮",
    "Camerún": "🇨🇲", "Ghana": "🇬🇭", "Senegal": "🇸🇳",
    "Marruecos": "🇲🇦", "Egipto": "🇪🇬", "Túnez": "🇹🇳",
    "Sudáfrica": "🇿🇦", "Australia": "🇦🇺", "Croacia": "🇭🇷",
    "Serbia": "🇷🇸", "Suiza": "🇨🇭", "Bélgica": "🇧🇪",
    "Dinamarca": "🇩🇰", "Suecia": "🇸🇪", "Noruega": "🇳🇴",
    "Polonia": "🇵🇱", "Turquía": "🇹🇷", "Grecia": "🇬🇷",
    "Irlanda": "🇮🇪", "Escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿"
}

POSICIONES = {
    "DEL": "⚽ Delantero",
    "MED": "🎯 Mediocampista",
    "DEF": "🛡️ Defensor",
    "POR": "🧤 Portero"
}

class ClubSelect(discord.ui.Select):
    def __init__(self, clubes, user_id):
        self.user_id = user_id
        self.clubes = clubes  # Guardamos la lista original para el callback
        options = []
        for i, c in enumerate(clubes[:25]):
            nombre_corto = c["nombre"][:80]
            options.append(discord.SelectOption(
                label=nombre_corto,
                description=f"{c['pais']} — {c['estadio'][:50]}",
                value=str(i)
            ))
        super().__init__(placeholder="Elige un club para fichar...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ No puedes interactuar con esto.", ephemeral=True)
            return

        idx = int(self.values[0])
        if idx >= len(self.clubes):
            await interaction.response.send_message("❌ Ese club ya no está disponible.", ephemeral=True)
            return

        await interaction.response.defer()

        club = self.clubes[idx]

        db.update_user(self.user_id, club_actual=club)

        embed = discord.Embed(
            title="✅ ¡FICHAJE COMPLETADO!",
            description=f"Has firmado un contrato con **{club['nombre']}** {club['pais']}",
            color=0x2ECC71
        )
        embed.add_field(name="🏟️ Estadio", value=club["estadio"], inline=True)
        embed.add_field(name="🌍 País", value=club["pais"], inline=True)

        # Check if player exists to update club in player dict
        data = db.get_user(self.user_id)
        if data.get("jugador"):
            jugador = data["jugador"]
            jugador["club"] = club["nombre"]
            db.update_user(self.user_id, jugador=jugador)

        # Check national team call-up after signing
        self.verificar_convocatoria(interaction, data)

        await interaction.edit_original_response(embed=embed, view=None)

    def verificar_convocatoria(self, interaction, data):
        jugador = data.get("jugador")
        if not jugador:
            return
        convocado = data.get("convocado_seleccion", False)
        if jugador["media"] >= 80 and not convocado:
            asyncio.create_task(self.enviar_convocatoria(interaction, jugador))

    async def enviar_convocatoria(self, interaction, jugador):
        db.update_user(self.user_id, convocado_seleccion=True)
        embed = discord.Embed(
            title="🇺🇳 ¡CONVOCATORIA A LA SELECCIÓN NACIONAL!",
            description=f"**{jugador['nombre']}** ha sido convocado a la Selección de **{jugador.get('pais_nombre', '')}** {jugador['pais']}",
            color=0x1ABC9C
        )
        embed.add_field(name="⭐ Media Actual", value=jugador["media"], inline=True)
        embed.add_field(name="📋 Posición", value=jugador.get("posicion_nombre", jugador["posicion"]), inline=True)
        try:
            canal = interaction.channel
            await canal.send(content=interaction.user.mention, embed=embed)
        except Exception:
            pass

class ClubView(discord.ui.View):
    def __init__(self, clubes, user_id):
        super().__init__()
        self.add_item(ClubSelect(clubes, user_id))


class BorrarJugadorView(discord.ui.View):
    def __init__(self, user_id, jugador):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.jugador = jugador

    @discord.ui.button(label="✅ Sí, borrar mi jugador", style=discord.ButtonStyle.danger, custom_id="borrar_confirm")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ No podés interactuar con esto.", ephemeral=True)
            return

        for child in self.children:
            child.disabled = True

        db.update_user(self.user_id, jugador=None, club_actual=None, convocado_seleccion=False)

        embed = discord.Embed(
            title="🗑️ JUGADOR BORRADO",
            description=f"**{self.jugador['nombre']}** {self.jugador['pais']} ha sido retirado del fútbol.\n\n"
                        "💰 Tus monedas, plantilla e insignias se mantienen.\n"
                        "👤 Usá `/crear_jugador` para empezar de nuevo.",
            color=0x95A5A6
        )
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary, custom_id="borrar_cancel")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ No podés interactuar con esto.", ephemeral=True)
            return

        for child in self.children:
            child.disabled = True

        embed = discord.Embed(
            title="✅ Operación Cancelada",
            description="Tu jugador sigue activo. ¡A seguir compitiendo!",
            color=0x2ECC71
        )
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        self.stop()


def aumentar_media_jugador(user_id, incremento):
    data = db.get_user(user_id)
    jugador = data.get("jugador")
    if not jugador:
        return None

    exp = jugador.get("experiencia", 0.0) + incremento
    media = jugador["media"]
    subio = False

    while exp >= 1.0 and media < 99:
        media += 1
        exp -= 1.0
        subio = True

    jugador["media"] = media
    jugador["experiencia"] = exp
    db.update_user(user_id, jugador=jugador)

    # Check national team call-up
    if media >= 80 and not data.get("convocado_seleccion", False):
        db.update_user(user_id, convocado_seleccion=True)
        return "convocado"

    return "subio" if subio else "ok"


class ModoCarrera(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_division(self, puntos):
        if puntos < 100:
            return DIVISIONES[0]
        elif puntos < 300:
            return DIVISIONES[1]
        elif puntos < 600:
            return DIVISIONES[2]
        else:
            return DIVISIONES[3]

    def get_progreso_division(self, puntos):
        limites = [100, 300, 600, float('inf')]
        umbrales = [100, 200, 300, 0]
        for i, lim in enumerate(limites):
            if puntos < lim:
                anterior = limites[i-1] if i > 0 else 0
                return barra_progreso(puntos - anterior, lim - anterior), puntos - anterior, lim - anterior
        return "▓" * 10, 0, 0

    def verificar_insignias(self, user_id):
        data = db.get_user(user_id)
        puntos = data.get("puntos", 0)
        victorias = data.get("victorias", 0)
        derrotas = data.get("derrotas", 0)
        equipo = data.get("equipo", [])
        jugador = data.get("jugador")
        saldo = data.get("monedas", 1000)
        racha_v = data.get("racha_victorias", 0)
        subastas = data.get("subastas_ganadas", 0)
        nuevas = []

        checks = [
            (victorias >= 1, "primera_victoria", "🎖️ Primera Victoria"),
            (racha_v >= 5, "invicto_5", "🛡️ Invencible"),
            (puntos >= 600, "ascenso_d1", "👑 Élite Absoluta"),
            (len(equipo) >= 5, "coleccionista", "📦 Coleccionista"),
            (jugador and jugador.get("goles", 0) >= 10, "goleador", "⚽ Goleador"),
            (saldo >= 5000, "millonario", "💰 Millonario"),
            (subastas >= 3, "subasta_rey", "👑 Rey de Subastas")
        ]

        for cond, ins_id, ins_nombre in checks:
            if cond and ins_id not in data.get("insignias", []):
                ok, reward = db.add_insignia(user_id, ins_id)
                if ok:
                    txt = ins_nombre
                    if reward > 0:
                        txt += f" (+{reward}💰)"
                    nuevas.append(txt)

        return nuevas

    # --- AUTOCOMPLETE ---
    async def pais_autocomplete(self, interaction: discord.Interaction, current: str):
        matches = [p for p in PAISES if current.lower() in p.lower()]
        return [
            app_commands.Choice(name=f"{PAISES[p]} {p}", value=p)
            for p in matches[:25]
        ]

    # --- COMANDOS NUEVOS ---
    @app_commands.command(name="crear_jugador", description="👤 Crear tu jugador para el Modo Carrera")
    @app_commands.autocomplete(pais=pais_autocomplete)
    @app_commands.choices(posicion=[
        app_commands.Choice(name="⚽ Delantero (DEL)", value="DEL"),
        app_commands.Choice(name="🎯 Mediocampista (MED)", value="MED"),
        app_commands.Choice(name="🛡️ Defensor (DEF)", value="DEF"),
        app_commands.Choice(name="🧤 Portero (POR)", value="POR")
    ])
    async def crear_jugador(self, interaction: discord.Interaction, nombre: str, pais: str, posicion: app_commands.Choice[str]):
        user_id = interaction.user.id
        data = db.get_user(user_id)

        if data.get("jugador"):
            await interaction.response.send_message("❌ Ya tienes un jugador creado. Usa `/mi_jugador` para verlo.", ephemeral=True)
            return

        pais_flag = PAISES.get(pais, "🌍")
        pos_nombre = POSICIONES.get(posicion.value, posicion.name)

        jugador = {
            "nombre": nombre,
            "pais": pais_flag,
            "pais_nombre": pais,
            "posicion": posicion.value,
            "posicion_nombre": pos_nombre,
            "media": 70,
            "experiencia": 0.0,
            "goles": 0,
            "partidos": 0,
            "club": "Sin club",
            "asistencias": 0
        }

        db.update_user(user_id, jugador=jugador)

        embed = discord.Embed(
            title="👤 ¡JUGADOR CREADO!",
            description=f"**{nombre}** {pais_flag} — ¡Bienvenido al fútbol profesional!",
            color=0x3498DB
        )
        embed.add_field(name="🌍 País", value=f"{pais_flag} {pais}", inline=True)
        embed.add_field(name="📋 Posición", value=pos_nombre, inline=True)
        embed.add_field(name="⭐ Media Inicial", value="**70**", inline=True)
        embed.add_field(name="💡 Sugerencia", value="Usa `/fichar` para firmar con un club y comenzar tu carrera.", inline=False)

        await interaction.response.send_message(embed=embed)

        # Auto-show clubs from their country
        clubes_disponibles = db.get_clubes_por_pais(pais_flag)
        if clubes_disponibles:
            await asyncio.sleep(1)
            embed2 = discord.Embed(
                title="🏟️ CLUBES DISPONIBLES EN TU PAÍS",
                description=f"Estos clubes de **{pais}** {pais_flag} están interesados en ti:",
                color=0xF1C40F
            )
            for c in clubes_disponibles[:10]:
                embed2.add_field(name=c["nombre"], value=f"🏟️ {c['estadio']}", inline=True)

            embed2.set_footer(text="Selecciona un club en el menú desplegable de abajo")
            view = ClubView(clubes_disponibles, user_id)
            await interaction.followup.send(embed=embed2, view=view)

    @app_commands.command(name="mi_jugador", description="👤 Ver tu jugador y su progreso en la carrera")
    async def mi_jugador(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        jugador = data.get("jugador")

        if not jugador:
            await interaction.response.send_message("❌ No tienes un jugador creado. Usa `/crear_jugador`.", ephemeral=True)
            return

        club = data.get("club_actual")
        convocado = data.get("convocado_seleccion", False)

        exp_actual = jugador.get("experiencia", 0.0)
        progreso = int((exp_actual / 1.0) * 100)
        barra = "🟩" * (progreso // 10) + "⬜" * max(0, 10 - progreso // 10)

        embed = discord.Embed(
            title=f"👤 {jugador['nombre']} {jugador['pais']}",
            description=f"**{jugador.get('posicion_nombre', jugador['posicion'])}** | ⭐ **{jugador['media']}**",
            color=0x3498DB
        )

        skin = data.get("skin_estadio")
        if club:
            nombre_club = club['nombre']
            if skin:
                nombre_club += f" 🏟️ *{skin}*"
            embed.add_field(name="🏟️ Club", value=f"{nombre_club} {club['pais']}", inline=True)
        else:
            embed.add_field(name="🏟️ Club", value="❌ Sin club", inline=True)

        embed.add_field(name="⚽ Partidos", value=str(jugador.get("partidos", 0)), inline=True)
        embed.add_field(name="🥅 Goles", value=str(jugador.get("goles", 0)), inline=True)
        embed.add_field(name="🎯 Asistencias", value=str(jugador.get("asistencias", 0)), inline=True)

        if convocado:
            embed.add_field(name="🇺🇳 Selección", value=f"✅ ¡Convocado a **{jugador.get('pais_nombre', 'tu país')}** {jugador['pais']}!", inline=False)
        else:
            embed.add_field(name="🇺🇳 Selección", value=f"⏳ Llega a media **80** para ser convocado (actual: {jugador['media']})", inline=False)

        embed.add_field(
            name="📈 Progreso a próxima media",
            value=f"{barra} `{progreso}%`",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fichar", description="🏟️ Ver clubes disponibles para fichar en tu país")
    async def fichar(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        jugador = data.get("jugador")

        if not jugador:
            await interaction.response.send_message("❌ Crea un jugador primero con `/crear_jugador`.", ephemeral=True)
            return

        pais_flag = jugador["pais"]
        items = data.get("items", [])
        tiene_mejora = "mejora_club" in items

        if tiene_mejora:
            clubes = db.get_clubes()
            titulo = "⭐ MERCADO GLOBAL (Mejora de Club Activa)"
        else:
            clubes = db.get_clubes_por_pais(pais_flag)
            titulo = f"🏟️ MERCADO DE FICHAJES"

        if not clubes:
            await interaction.response.send_message(f"❌ No hay clubes disponibles.", ephemeral=True)
            return

        embed = discord.Embed(
            title=titulo,
            description=f"Clubes disponibles para {jugador.get('pais_nombre', '')} {pais_flag}:" if not tiene_mejora else "🌍 **Todos los clubes del mundo están disponibles gracias a tu Mejora de Club!**",
            color=0xF1C40F
        )
        for c in clubes[:10]:
            embed.add_field(name=c["nombre"], value=f"🏟️ {c['estadio']}", inline=True)

        embed.set_footer(text="Selecciona un club para firmar contrato")
        view = ClubView(clubes, user_id)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="crear_club", description="🏟️ Crear un nuevo club disponible para todos los jugadores")
    @app_commands.autocomplete(pais=pais_autocomplete)
    async def crear_club(self, interaction: discord.Interaction, nombre: str, pais: str, estadio: str):
        user_id = interaction.user.id
        data = db.get_user(user_id)

        if not data.get("jugador"):
            await interaction.response.send_message("❌ Crea un jugador primero con `/crear_jugador`.", ephemeral=True)
            return

        pais_flag = PAISES.get(pais, "🌍")

        club_data = {
            "nombre": nombre,
            "pais": pais_flag,
            "estadio": estadio
        }

        db.add_club(club_data)

        embed = discord.Embed(
            title="🏟️ ¡CLUB CREADO!",
            description=f"**{nombre}** {pais_flag} ahora está disponible para todos los jugadores en el mercado de fichajes.",
            color=0x9B59B6
        )
        embed.add_field(name="🏟️ Estadio", value=estadio, inline=True)
        embed.add_field(name="🌍 País", value=f"{pais_flag} {pais}", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clubes", description="🏟️ Ver todos los clubes disponibles en el mundo")
    async def clubes(self, interaction: discord.Interaction):
        clubes = db.get_clubes()

        if not clubes:
            await interaction.response.send_message("❌ No hay clubes registrados.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🏟️ CLUBES DISPONIBLES — FUTROL",
            description=f"Hay **{len(clubes)}** clubes en el mundo de FUTROL.",
            color=0x2ECC71
        )

        por_pais = {}
        for c in clubes:
            p = c["pais"]
            if p not in por_pais:
                por_pais[p] = []
            por_pais[p].append(c["nombre"])

        for pais, clubs in sorted(por_pais.items(), key=lambda x: -len(x[1]))[:10]:
            lista = ", ".join(clubs[:5])
            if len(clubs) > 5:
                lista += f" y {len(clubs)-5} más..."
            embed.add_field(name=f"{pais} ({len(clubs)})", value=lista, inline=False)

        embed.set_footer(text="Usa /fichar para unirte a un club de tu país")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="seleccion", description="🇺🇳 Ver tu estado en la selección nacional")
    async def seleccion(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        jugador = data.get("jugador")

        if not jugador:
            await interaction.response.send_message("❌ Crea un jugador primero con `/crear_jugador`.", ephemeral=True)
            return

        convocado = data.get("convocado_seleccion", False)

        embed = discord.Embed(
            title=f"🇺🇳 SELECCIÓN NACIONAL — {jugador.get('pais_nombre', '')} {jugador['pais']}",
            color=0x1ABC9C
        )

        if convocado:
            embed.description = f"**{jugador['nombre']}** es internacional absoluto con **{jugador.get('pais_nombre', 'tu país')}** {jugador['pais']}."
            embed.add_field(name="⭐ Media", value=jugador["media"], inline=True)
            embed.add_field(name="📋 Posición", value=jugador.get("posicion_nombre", jugador["posicion"]), inline=True)
            embed.add_field(name="⚽ Partidos con selección", value=str(jugador.get("partidos_seleccion", 0)), inline=True)
            embed.add_field(name="🥅 Goles con selección", value=str(jugador.get("goles_seleccion", 0)), inline=True)
        else:
            embed.description = f"**{jugador['nombre']}** aún no ha sido convocado.\nNecesitas alcanzar **media 80** para ser llamado a la selección."
            embed.add_field(name="⭐ Media Actual", value=jugador["media"], inline=True)
            embed.add_field(name="📈 Progreso", value=f"{jugador['media']}/80 — {'Falta ' + str(80 - jugador['media']) + ' puntos' if jugador['media'] < 80 else '¡Ya cumples el requisito!'}", inline=False)

        await interaction.response.send_message(embed=embed)

    # --- COMANDOS EXISTENTES MODIFICADOS ---
    @app_commands.command(name="carrera", description="🏆 Ver tu progreso en el Modo Carrera")
    async def carrera(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)

        puntos = data.get("puntos", 0)
        victorias = data.get("victorias", 0)
        derrotas = data.get("derrotas", 0)
        equipo = data.get("equipo", [])
        jugador = data.get("jugador")
        insignias = data.get("insignias", [])

        embed = discord.Embed(
            title=f"🏆 MODO CARRERA — {interaction.user.display_name}",
            color=0xFFD700
        )

        if jugador:
            embed.description = f"👤 **{jugador['nombre']}** {jugador['pais']} — {jugador.get('posicion_nombre', jugador['posicion'])} ⭐{jugador['media']}"
        else:
            embed.description = "Administra tu equipo y jugador."

        skin = data.get("skin_estadio")
        if skin:
            embed.add_field(name="🏟️ Estadio", value=skin, inline=False)

        embed.add_field(name="📋 División Actual", value=f"**{self.get_division(puntos)}**", inline=True)
        embed.add_field(name="🏆 Temporada", value=f"**{data.get('temporada', 1)}**", inline=True)

        if puntos < 600:
            barra, act, maxi = self.get_progreso_division(puntos)
            embed.add_field(name="📈 Progreso a próxima división", value=f"{barra} `{act}/{maxi} pts`", inline=False)

        embed.add_field(name="⭐ Puntos", value=f"`{puntos}` pts", inline=True)
        embed.add_field(name="✅ Victorias", value=f"`{victorias}` victorias", inline=True)
        embed.add_field(name="❌ Derrotas", value=f"`{derrotas}` derrotas", inline=True)
        embed.add_field(name="👕 Plantilla", value=f"`{len(equipo)}` jugadores", inline=True)

        if insignias:
            embed.add_field(name="🎖️ Insignias", value=" | ".join(insignias), inline=False)

        if not jugador:
            embed.add_field(name="💡 ¿Sin jugador?", value="Usa `/crear_jugador` para iniciar tu carrera como futbolista.", inline=False)

        embed.set_footer(text="FUTROL — Usa /jugar_partido para competir")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="entrenar", description="💪 Entrenar para ganar monedas, puntos y subir tu media (cooldown 2h)")
    async def entrenar(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)

        ultimo_entreno = data.get("ultimo_entrenamiento", 0.0)
        ahora = time.time()
        cooldown_segundos = 7200

        tiempo_pasado = ahora - ultimo_entreno
        if tiempo_pasado < cooldown_segundos:
            tiempo_restante = cooldown_segundos - tiempo_pasado
            minutos = int(tiempo_restante // 60)
            segundos = int(tiempo_restante % 60)
            await interaction.response.send_message(
                f"❌ Tu equipo está agotado. Debes esperar **{minutos}m {segundos}s** para volver a entrenar. ⏳",
                ephemeral=True
            )
            return

        monedas_ganadas = random.randint(30, 80)
        puntos_ganados = random.randint(4, 8)

        boost = data.get("train_boost", 0)
        if boost > 0:
            monedas_ganadas *= 2
            puntos_ganados *= 2
            db.update_user(user_id, train_boost=boost - 1)
            boost_text = " (x2 por Boost de Entreno!)"
        else:
            boost_text = ""

        nuevos_puntos = data.get("puntos", 0) + puntos_ganados
        db.update_user(user_id, puntos=nuevos_puntos, ultimo_entrenamiento=ahora)
        db.add_saldo(user_id, monedas_ganadas)

        embed = discord.Embed(
            title="💪 ENTRENAMIENTO COMPLETADO",
            description=f"¡Tu equipo ha completado la sesión táctica y física de hoy!{boost_text}",
            color=0x3498DB
        )
        embed.add_field(name="💰 Monedas", value=f"`+{monedas_ganadas} monedas`", inline=True)
        embed.add_field(name="⭐ Puntos", value=f"`+{puntos_ganados} pts`", inline=True)
        embed.add_field(name="📋 Nueva División", value=self.get_division(nuevos_puntos), inline=False)

        # Player media progression
        jugador = data.get("jugador")
        if jugador:
            resultado = aumentar_media_jugador(user_id, 0.33)
            data_actualizada = db.get_user(user_id)
            jugador_nuevo = data_actualizada.get("jugador")
            if resultado == "convocado":
                embed.add_field(
                    name="🇺🇳 ¡CONVOCATORIA!",
                    value=f"¡Has sido convocado a la selección de **{jugador_nuevo.get('pais_nombre', '')}** {jugador_nuevo['pais']}!",
                    inline=False
                )
            elif jugador_nuevo:
                embed.add_field(
                    name="📈 Progreso del Jugador",
                    value=f"⭐ Media: **{jugador_nuevo['media']}** | 📊 Experiencia: `{int(jugador_nuevo.get('experiencia',0)*100)}%` para la próxima",
                    inline=False
                )
                if resultado == "subio":
                    embed.add_field(name="⬆️ ¡MEDIA SUBIDA!", value=f"¡Ahora tu jugador tiene **{jugador_nuevo['media']}** de media!", inline=False)

        nuevas_insignias = self.verificar_insignias(user_id)
        if nuevas_insignias:
            embed.add_field(
                name="🎖️ ¡NUEVAS INSIGNIAS!",
                value="\n".join([f"✅ {i}" for i in nuevas_insignias]),
                inline=False
            )

        embed.set_footer(text="FUTROL — Entrenar mejora tu rendimiento en partidos")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="posiciones", description="📋 Administrar las posiciones de tus jugadores en la plantilla")
    async def posiciones(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        equipo = data.get("equipo", [])

        if not equipo:
            await interaction.response.send_message("❌ No tenés jugadores en tu plantilla. Ganá subastas con `/subasta`.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📋 POSICIONES DE TU PLANTILLA",
            description=f"Tenés **{len(equipo)}** jugadores en tu club.",
            color=0x3498DB
        )

        por_posicion = {}
        for j in equipo:
            pos = j.get("posicion", "N/A")
            if pos not in por_posicion:
                por_posicion[pos] = []
            por_posicion[pos].append(j)

        for pos, jugadores in sorted(por_posicion.items()):
            lista = "\n".join([f"• {j['nombre']} ⭐{j['ovr']}" for j in jugadores])
            embed.add_field(name=f"{pos} ({len(jugadores)})", value=lista, inline=False)

        embed.set_footer(text="FUTROL — Usá /subasta para fichar más jugadores")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="jugar_partido", description="⚽ Simular un partido — tu media influye en el resultado")
    @app_commands.choices(estrategia=[
        app_commands.Choice(name="🛡️ Defensiva (Menos goles encajados, menor ataque)", value="defensiva"),
        app_commands.Choice(name="⚖️ Equilibrada (Balanceada)", value="equilibrada"),
        app_commands.Choice(name="⚔️ Ofensiva (Ataque total, riesgo en defensa)", value="ofensiva")
    ])
    async def jugar_partido(self, interaction: discord.Interaction, estrategia: app_commands.Choice[str]):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        jugador = data.get("jugador")

        # Cooldown de 30 minutos
        ahora = time.time()
        ultimo = data.get("ultimo_partido", 0.0)
        cooldown = 1800
        if ahora - ultimo < cooldown:
            restante = cooldown - (ahora - ultimo)
            mins = int(restante // 60)
            segs = int(restante % 60)
            await interaction.response.send_message(
                f"⏳ Esperá **{mins}m {segs}s** antes de jugar otro partido.",
                ephemeral=True
            )
            return

        db.update_user(user_id, ultimo_partido=ahora)

        media_jugador = jugador["media"] if jugador else 75
        rival = random.choice(OPONENTES)
        est_nombre = estrategia.name
        est_valor = estrategia.value

        embed = discord.Embed(
            title="⚽ ¡PARTIDO EN CURSO! ⚽",
            description=f"**Tu equipo** se enfrenta a **{rival}**.\nEstrategia: **{est_nombre}**",
            color=0xE67E22
        )
        if jugador:
            embed.add_field(name="👤 Tu Jugador", value=f"{jugador['nombre']} {jugador['pais']} ⭐{jugador['media']}", inline=False)
        embed.add_field(name="⏱️ Estado", value="¡Comienza el pitido inicial!", inline=False)
        embed.set_footer(text="Simulación en tiempo real • FUTROL")

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()

        # ---- MINUTO 30 ----
        await asyncio.sleep(2.5)
        comentarios_1 = [
            "El rival domina la posesión en el mediocampo buscando espacios.",
            "¡Tu defensa realiza un corte impecable frustrando la contra del rival!",
            "¡Gran jugada colectiva que termina en un centro al área!",
            "Falta dura en el círculo central, el árbitro advierte verbalmente."
        ]
        if jugador:
            comentarios_1.append(f"**{jugador['nombre']}** recibe el balón y gira buscando hueco. ¡Espectacular control orientado!")
            comentarios_1.append(f"**{jugador['nombre']}** habilita a un compañero con un pase filtrado al espacio.")
        embed.set_field_at(0 if not jugador else 1, name="⏱️ Minuto 30", value=random.choice(comentarios_1), inline=False)
        await msg.edit(embed=embed)

        # ---- MINUTO 70 ----
        await asyncio.sleep(2.5)
        comentarios_2 = [
            "¡Cabezazo peligroso en un tiro de esquina que roza el poste!",
            "El arquero rival realiza una atajada espectacular tras un disparo de larga distancia.",
            "¡Presión alta en la salida que obliga al error defensivo!",
            "Se preparan cambios tácticos en el banquillo."
        ]
        if jugador:
            if data.get("club_actual"):
                comentarios_2.append(f"La afición de **{data['club_actual']['nombre']}** corea el nombre de **{jugador['nombre']}**.")
            comentarios_2.append(f"**{jugador['nombre']}** pide el balón, se perfila y... ¡dispara! El arquero desvía al córner.")
        embed.set_field_at(0 if not jugador else 1, name="⏱️ Minuto 70", value=random.choice(comentarios_2), inline=False)
        await msg.edit(embed=embed)

        # ---- RESULTADO ----
        await asyncio.sleep(2.5)

        # Adjust weights based on player media
        if media_jugador >= 90:
            boost = 0.2
        elif media_jugador >= 80:
            boost = 0.1
        elif media_jugador >= 70:
            boost = 0.0
        else:
            boost = -0.1

        if est_valor == "defensiva":
            goles_propios = random.choices([0, 1, 2], weights=[0.5 - boost, 0.4 + boost, 0.1])[0]
            goles_rival = random.choices([0, 1, 2], weights=[0.6 + boost, 0.35 - boost, 0.05])[0]
        elif est_valor == "ofensiva":
            goles_propios = random.choices([0, 1, 2, 3, 4], weights=[0.1, 0.3 - boost, 0.35, 0.2 + boost, 0.05 + boost])[0]
            goles_rival = random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.3, 0.1 + boost * 0.5])[0]
        else:
            goles_propios = random.choices([0, 1, 2, 3], weights=[0.25 - boost, 0.45 + boost, 0.2, 0.1])[0]
            goles_rival = random.choices([0, 1, 2, 3], weights=[0.3 + boost, 0.45 - boost, 0.2, 0.05])[0]

        goles_propios = max(0, goles_propios)
        goles_rival = max(0, goles_rival)

        marcador = f"**Tu Equipo {goles_propios} — {goles_rival} {rival}**"

        puntos_actuales = data.get("puntos", 0)
        victorias = data.get("victorias", 0)
        derrotas = data.get("derrotas", 0)

        racha_v = data.get("racha_victorias", 0)

        if goles_propios > goles_rival:
            pts_cambio = 15
            monedas_cambio = 150
            resultado_texto = f"🏆 **¡VICTORIA ESPECTACULAR!** 🏆\nGanaste **{pts_cambio} pts** y **{monedas_cambio} monedas** 💰."
            nuevos_puntos = puntos_actuales + pts_cambio
            nueva_racha = racha_v + 1
            db.update_user(user_id, puntos=nuevos_puntos, victorias=victorias + 1, racha_victorias=nueva_racha)
            db.add_saldo(user_id, monedas_cambio)
            color_res = 0x2ECC71
            exp_partido = 0.8
        elif goles_propios < goles_rival:
            racha_v = 0
            proteccion = data.get("proteccion_puntos", False)
            if proteccion:
                pts_cambio = 0
                resultado_texto = f"🛡️ **DERROTA PROTEGIDA** 🛡️\nNo perdiste puntos gracias a tu protección."
                db.remove_item(user_id, "proteccion_puntos")
                db.update_user(user_id, proteccion_puntos=False)
            else:
                pts_cambio = -10
                resultado_texto = f"💔 **DERROTA** 💔\nPerdiste **10 puntos** de carrera."
            nuevos_puntos = max(0, puntos_actuales + pts_cambio)
            db.update_user(user_id, puntos=nuevos_puntos, derrotas=derrotas + 1, racha_victorias=racha_v)
            color_res = 0xE74C3C
            exp_partido = 0.2
        else:
            pts_cambio = 5
            monedas_cambio = 50
            resultado_texto = f"🤝 **EMPATE** 🤝\nGanas **{pts_cambio} pts** y **{monedas_cambio} monedas** 💰."
            nuevos_puntos = puntos_actuales + pts_cambio
            db.update_user(user_id, puntos=nuevos_puntos, racha_victorias=racha_v + 1)
            db.add_saldo(user_id, monedas_cambio)
            color_res = 0xF1C40F
            exp_partido = 0.5

        embed_fin = discord.Embed(
            title="⏱️ ¡FINAL DEL PARTIDO!",
            description=f"{marcador}\n\n{resultado_texto}",
            color=color_res
        )
        embed_fin.add_field(name="📋 Nueva División", value=self.get_division(nuevos_puntos), inline=True)
        embed_fin.add_field(name="⭐ Puntos Totales", value=f"`{nuevos_puntos}` pts", inline=True)

        # Player progression after match
        if jugador:
            goles_marcados = random.choices([0, 0, 0, 1, 1, 2], weights=[0.4, 0.2, 0.1, 0.15, 0.1, 0.05])[0] if goles_propios > 0 else 0
            asistencias = random.choices([0, 0, 0, 1, 1], weights=[0.6, 0.2, 0.1, 0.07, 0.03])[0] if goles_propios > 0 else 0

            jugador["partidos"] = jugador.get("partidos", 0) + 1
            jugador["goles"] = jugador.get("goles", 0) + goles_marcados
            jugador["asistencias"] = jugador.get("asistencias", 0) + asistencias
            db.update_user(user_id, jugador=jugador)

            resultado = aumentar_media_jugador(user_id, exp_partido)
            data_actualizada = db.get_user(user_id)
            jugador_nuevo = data_actualizada.get("jugador")

            stats_linea = ""
            if goles_marcados > 0:
                stats_linea += f"⚽ **{goles_marcados} gol{'es' if goles_marcados > 1 else ''}** "
            if asistencias > 0:
                stats_linea += f"🎯 **{asistencias} asistencia{'s' if asistencias > 1 else ''}** "
            if not stats_linea:
                stats_linea = "📊 Partido discreto en lo individual"

            embed_fin.add_field(
                name=f"👤 Actuación de {jugador_nuevo['nombre']}",
                value=stats_linea,
                inline=False
            )
            embed_fin.add_field(
                name="⭐ Media",
                value=f"**{jugador_nuevo['media']}** ({'+1' if resultado == 'subio' else 'estable'})",
                inline=True
            )
            embed_fin.add_field(name="⚽ Total Goles", value=str(jugador_nuevo.get("goles", 0)), inline=True)
            embed_fin.add_field(name="🎯 Asistencias", value=str(jugador_nuevo.get("asistencias", 0)), inline=True)

            if resultado == "convocado":
                embed_fin.add_field(
                    name="🇺🇳 ¡CONVOCATORIA!",
                    value=f"¡Has sido convocado a la selección de **{jugador_nuevo.get('pais_nombre', '')}** {jugador_nuevo['pais']}!",
                    inline=False
                )

        nuevas_insignias = self.verificar_insignias(user_id)
        if nuevas_insignias:
            embed_fin.add_field(
                name="🎖️ ¡NUEVAS INSIGNIAS!",
                value="\n".join([f"✅ {i}" for i in nuevas_insignias]),
                inline=False
            )

        import datetime
        resultado_str = "victoria" if goles_propios > goles_rival else "derrota" if goles_propios < goles_rival else "empate"
        db.add_match_history(user_id, {
            "rival": rival,
            "goles_favor": goles_propios,
            "goles_contra": goles_rival,
            "resultado": resultado_str,
            "division": self.get_division(nuevos_puntos),
            "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        })

        if nuevos_puntos >= 1000:
            temp = data.get("temporada", 1)
            db.update_user(user_id, temporada=temp + 1, puntos=0)
            embed_fin.add_field(
                name="🏆 ¡TEMPORADA COMPLETADA!",
                value=f"Completaste la **Temporada {temp}** con **{nuevos_puntos} pts**.\n"
                      f"¡Comenzás la **Temporada {temp + 1}** desde D4! Tus monedas y jugador se mantienen.",
                inline=False
            )

        embed_fin.set_footer(text="FUTROL — Usa /mi_jugador para ver tu progreso")
        await msg.edit(embed=embed_fin)

    @app_commands.command(name="borrar_jugador", description="🗑️ Borrar tu jugador del Modo Carrera (acción irreversible)")
    async def borrar_jugador(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        jugador = data.get("jugador")

        if not jugador:
            await interaction.response.send_message("❌ No tenés un jugador creado.", ephemeral=True)
            return

        view = BorrarJugadorView(user_id, jugador)
        embed = discord.Embed(
            title="⚠️ ¿ESTÁS SEGURO?",
            description=f"Vas a borrar a **{jugador['nombre']}** {jugador['pais']}.\n\n"
                        f"📊 Media: ⭐{jugador['media']}\n"
                        f"⚽ Goles: {jugador.get('goles', 0)}\n"
                        f"🎯 Asistencias: {jugador.get('asistencias', 0)}\n"
                        f"🏟️ Club: {jugador.get('club', 'Sin club')}\n\n"
                        "**Esta acción es irreversible.**\n"
                        "Tus monedas, plantilla de subasta e insignias NO se pierden.",
            color=0xE74C3C
        )
        embed.set_footer(text="FUTROL — Presioná Confirmar para borrar")
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="historial", description="📜 Ver el historial de tus últimos partidos")
    async def historial(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = db.get_user(user_id)
        historial = data.get("historial_partidos", [])

        if not historial:
            await interaction.response.send_message("📜 No tenés partidos registrados aún. Jugá con `/jugar_partido`.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📜 HISTORIAL — {interaction.user.display_name}",
            description=f"Últimos {len(historial)} partidos:",
            color=0x3498DB
        )

        for entry in reversed(historial[-10:]):
            emoji = "🏆" if entry["resultado"] == "victoria" else "🤝" if entry["resultado"] == "empate" else "💔"
            embed.add_field(
                name=f"{emoji} vs {entry['rival']}",
                value=f"**{entry['goles_favor']} - {entry['goles_contra']}** | 📋 {entry['division']} | ⏱️ {entry['fecha']}",
                inline=False
            )

        embed.set_footer(text="FUTROL — Seguí mejorando tu carrera")
        await interaction.response.send_message(embed=embed)

    # --- TOP ---
    @app_commands.command(name="carrera_top", description="👑 Ver el Top 10 de mejores mánagers del servidor")
    async def carrera_top(self, interaction: discord.Interaction):
        leaderboard = db.get_leaderboard(limit=10)

        embed = discord.Embed(
            title="👑 LÍDERES DE MODO CARRERA — FUTROL",
            description="Ranking de los mejores directores técnicos en el servidor.",
            color=0xFFD700
        )

        if not leaderboard:
            embed.description = "Aún no hay mánagers registrados en el ranking."
        else:
            descripcion = ""
            for i, manager in enumerate(leaderboard, 1):
                user_mention = f"<@{manager['id']}>"
                puntos = manager["puntos"]
                v = manager["victorias"]
                d = manager["derrotas"]

                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"`{i}.`"
                descripcion += f"{emoji} {user_mention} — **{puntos} pts** (W: `{v}` | L: `{d}`)\n"

            embed.description = descripcion

        embed.set_footer(text="FUTROL — Compite y sube en la clasificación")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ModoCarrera(bot))
