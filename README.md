
<p align="center">
  <img src="https://img.icons8.com/color/96/football2.png" alt="FUTROL Logo"/>
</p>

<h1 align="center">⚽ FUTROL — El Bot Definitivo del Fútbol</h1>

<p align="center">
  <strong>El bot más completo para servidores de fútbol en Discord.</strong><br>
  Subastas de cracks, modo carrera, trivias épicas, torneos entre miembros, duelos 1v1 y más.
</p>

<p align="center"><em>Discord bot de fútbol todo-en-uno: subastas, modo carrera, trivias, torneos, economía, duelos y más.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/versión-10/10-2ecc71?style=flat-square"/>
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/discord.py-2.3+-blueviolet?style=flat-square"/>
  <img src="https://img.shields.io/badge/licencia-MIT-green?style=flat-square"/>
</p>

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Comandos](#-comandos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Despliegue 24/7](#-despliegue-247)
- [Tecnologías](#-tecnologías)
- [Créditos](#-créditos)

---

## 🚀 Características

### 🥅 Juegos y Desafíos
- **Penales** — Pateá penales con botones, sistema de rachas (cada 3 seguidos = premio doble)
- **Trivia** — +300 preguntas de fútbol con botones y recompensas
- **Impostor** — Juego de deducción social futbolero con DMs de roles

### 🔮 Mercado y Colección
- **Subasta** — Jugadores misteriosos con rareza (Oro/Plata/Bronce), snipe protection
- **Mercado de Transferencias** — Vende y compra jugadores entre usuarios
- **Plantilla** — Administrá tus jugadores y sus posiciones

### 🏆 Modo Carrera
- Creá tu jugador, fichá por clubes, entrená y competí
- **4 divisiones** (D4 Bronce → D1 Élite)
- **Sistema de temporadas** — Al llegar a 1000 pts, nueva temporada
- **Insignias** con recompensas en monedas al desbloquear
- **Historial** de partidos guardado

### 💰 Economía
- Sistema de monedas completo con saldo, perfil y ranking
- **Recompensa diaria** con racha creciente (hasta +400💰/día)
- **Tienda** con items comprables: boost de entreno, protección de puntos, mejora de club, boost de subasta
- Transferencias entre usuarios

### ⚔️ Duelos y Versus
- **Retar** — Duelo de penales 1v1 con elección secreta
- **Trivia Duelo** — 5 preguntas, quien responde primero gana

### 🎯 Predicciones
- Creá predicciones de partidos reales (admin)
- Los usuarios votan su resultado
- Los acertantes ganan monedas

### 🏆 Torneos
- Creá torneos con apuesta por participante
- Brackets automáticos, simulación ronda por ronda
- El campeón se lleva todo el pozo

---

## 📚 Comandos

### 🥅 Juegos
| Comando | Descripción |
|---------|-------------|
| `/penal` | Pateá un penal por monedas |
| `/trivia` | Respondé preguntas de fútbol (+100💰) |
| `/impostor` | Iniciá el juego del impostor |

### 🔮 Subastas
| Comando | Descripción |
|---------|-------------|
| `/subasta` | Iniciá una subasta de jugador misterioso |
| `/apostar [cantidad]` | Pujá en la subasta activa |
| `/mequipo` | Revisá tu plantilla de jugadores |
| `/posiciones` | Ver jugadores por posición |

### 🏆 Modo Carrera
| Comando | Descripción |
|---------|-------------|
| `/crear_jugador` | Creá tu jugador para el modo carrera |
| `/mi_jugador` | Ver tu jugador y progreso |
| `/fichar` | Firmá con un club |
| `/jugar_partido [estrategia]` | Simulá un partido (cooldown 30min) |
| `/entrenar` | Entrená para ganar monedas y puntos (cooldown 2h) |
| `/carrera` | Ver tu progreso en la carrera |
| `/carrera_top` | Top 10 del servidor |
| `/historial` | Últimos partidos jugados |
| `/borrar_jugador` | Borrar tu jugador (con confirmación) |
| `/seleccion` | Estado en la selección nacional |
| `/crear_club` | Crear un nuevo club |
| `/clubes` | Ver todos los clubes disponibles |

### 💰 Economía
| Comando | Descripción |
|---------|-------------|
| `/saldo` | Ver monedas y estadísticas |
| `/perfil` | Perfil completo del mánager |
| `/diario` | Recompensa diaria (24h, con racha) |
| `/transferir @user cantidad` | Transferir monedas |
| `/tienda` | Comprar mejoras |
| `/usar_item` | Activar un item del inventario |
| `/top_ricos` | Ranking de los más ricos |

### 🏪 Mercado
| Comando | Descripción |
|---------|-------------|
| `/mercado` | Ver jugadores en venta |
| `/vender precio` | Vender un jugador |
| `/comprar id` | Comprar un jugador |

### ⚔️ Duelos
| Comando | Descripción |
|---------|-------------|
| `/retar @user [apuesta]` | Duelo de penales 1v1 |
| `/trivia_duelo @user [apuesta]` | Duelo de trivia |

### 🎯 Predicciones
| Comando | Descripción |
|---------|-------------|
| `/predecir local visitante` | Crear predicción (admin) |
| `/predicciones_activas` | Ver predicciones abiertas |
| `/cerrar_prediccion id resultado` | Cerrar predicción (admin) |

### 🏆 Torneos
| Comando | Descripción |
|---------|-------------|
| `/torneo_crear nombre apuesta` | Crear torneo (admin) |
| `/torneo_unirse` | Unirse al torneo activo |
| `/torneo_iniciar` | Iniciar el torneo (admin) |

### ℹ️ Información
| Comando | Descripción |
|---------|-------------|
| `/reglas` | Reglas del servidor |
| `/ayuda` | Panel de ayuda completo |
| `/info` | Info del bot, creadores y versión |

---

## 📁 Estructura del Proyecto

```
FUTROL/
├── main.py              # Punto de entrada del bot
├── .env                 # Token de Discord (no subir a GitHub)
├── .gitignore           # Archivos ignorados por git
├── README.md            # Este archivo
│
├── cogs/
│   ├── penales.py       # 🥅 Juego de penales
│   ├── trivia.py        # 🧠 Trivia futbolera (300+ preguntas)
│   ├── impostor.py      # 🕵️ Juego del impostor
│   ├── subasta.py       # 🔮 Subasta de jugadores
│   ├── carrera.py       # 🏆 Modo carrera completo
│   ├── reglas.py        # 📜 Reglas, ayuda e info
│   ├── economia.py      # 💰 Economía, tienda, mercado
│   ├── versus.py        # ⚔️ Duelos 1v1
│   ├── predicciones.py  # 🎯 Predicciones de partidos
│   └── torneos.py       # 🏆 Torneos automáticos
│
├── utils/
│   └── db.py            # Base de datos JSON
│
└── data/
    └── db.json          # Datos persistentes (usuarios, clubes, etc.)
```

---

## 🔧 Instalación

### Requisitos
- Python 3.10 o superior
- pip (gestor de paquetes)

### Pasos

1. **Cloná el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/FUTROL.git
   cd FUTROL
   ```

2. **Instalá las dependencias**
   ```bash
   pip install -r requirements.txt
   ```
   *(Si no tenés `requirements.txt`, instalá manualmente: `pip install discord.py python-dotenv`)*

3. **Configurá el token**
   - Creá un archivo `.env` en la raíz del proyecto
   - Agregá tu token de Discord:
     ```
     DISCORD_TOKEN=tu_token_aqui
     ```
   *(Obtené tu token en https://discord.com/developers/applications)*

4. **Invitá el bot a tu servidor**
   - En el Portal de Desarrolladores de Discord → OAuth2 → URL Generator
   - Seleccioná `bot` y `applications.commands`
   - Permisos: `Send Messages`, `Embed Links`, `Read Message History`, `Use Slash Commands`

5. **Ejecutá el bot**
   ```bash
   python main.py
   ```

---

## ☁️ Despliegue 24/7

Tenés varias opciones para mantener el bot 24/7. Ordenadas de recomendada a menos recomendada:

| Opción | Costo | Tipo |
|--------|-------|------|
| **VPS propio** (Oracle Cloud Free Tier, Hetzner, DigitalOcean) | Gratis o €3-5/mes | Instancia Linux completa, 24/7 real |
| **Docker** | Según host | Contenedor portable |
| **Servicios cloud** (Railway, Fly.io, PythonAnywhere) | Gratis limitado o pago | Pueden dormir o requerir tarjeta |

> **⚠️** Si el bot se apaga por inactividad o falta de persistencia de datos, perdés progreso. Un VPS es la solución más confiable.

### Opción 4: Raspberry Pi en tu casa

```bash
# En tu Raspberry Pi
sudo apt install python3 python3-pip git -y
git clone https://github.com/tu-usuario/FUTROL.git
cd FUTROL
pip3 install -r requirements.txt

# Con screen o tmux para mantenerlo corriendo
sudo apt install screen -y
screen -S futrol
python3 main.py
# Ctrl+A, D para desconectarte (el bot sigue corriendo)
```

---

## 🛠️ Tecnologías

- **[discord.py](https://github.com/Rapptz/discord.py)** — Librería de Discord para Python
- **[Python 3.10+](https://python.org/)** — Lenguaje de programación
- **JSON** — Base de datos ligera (persistencia en archivo)

---

## 👥 Créditos

| | |
|---|-----|
| 👨‍💻 **Creadores** | **ancestors_kant** & **Exxe** |
| ⚽ **Versión** | 10/10 — Mejora Total |
| 🐛 **Reportar bugs** | [Abrir issue](https://github.com/tu-usuario/FUTROL/issues) |

---

<p align="center">
  <strong>FUTROL — Donde el fútbol y Discord se encuentran ⚽</strong><br>
  <sub>Hecho con ❤️ para la comunidad futbolera</sub>
</p>
