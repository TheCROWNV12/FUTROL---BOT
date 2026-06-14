# utils/db.py
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db.json")

INSIGNIAS_POR_DEFECTO = [
    {"id": "primera_victoria", "nombre": "🎖️ Primera Victoria", "desc": "Ganá tu primer partido en el Modo Carrera"},
    {"id": "invicto_5", "nombre": "🛡️ Invencible", "desc": "Ganá 5 partidos seguidos sin perder"},
    {"id": "ascenso_d1", "nombre": "👑 Élite Absoluta", "desc": "Ascendé a la División 1"},
    {"id": "coleccionista", "nombre": "📦 Coleccionista", "desc": "Acumulá 5 jugadores en tu plantilla"},
    {"id": "goleador", "nombre": "⚽ Goleador", "desc": "Marcá 10 goles con tu jugador"},
    {"id": "millonario", "nombre": "💰 Millonario", "desc": "Acumulá 5000 monedas"},
    {"id": "racha_diaria_7", "nombre": "🔥 Fiel Mánager", "desc": "Reclamá el diario 7 días consecutivos"},
    {"id": "subasta_rey", "nombre": "👑 Rey de Subastas", "desc": "Ganá 3 subastas"}
]

ITEMS_TIENDA = [
    {"id": "boost_entreno", "nombre": "🏋️ Boost de Entreno", "desc": "Duplica las ganancias del próximo entrenamiento", "precio": 200},
    {"id": "skin_estadio", "nombre": "🏟️ Skin de Estadio", "desc": "Personalizá tu estadio (estético)", "precio": 500},
    {"id": "proteccion_puntos", "nombre": "🛡️ Protección de Puntos", "desc": "No perdés puntos en tu próxima derrota", "precio": 300},
    {"id": "mejora_club", "nombre": "⭐ Mejora de Club", "desc": "Desbloqueá clubes de nivel superior para fichar", "precio": 800},
    {"id": "boost_subasta", "nombre": "💰 Boost de Subasta", "desc": "Recibí 500 monedas extra al ganar una subasta", "precio": 400}
]

CLUBES_POR_DEFECTO = [
    {"nombre": "Argentinos Juniors", "pais": "🇦🇷", "estadio": "Estadio Diego Armando Maradona"},
    {"nombre": "Lanús", "pais": "🇦🇷", "estadio": "Estadio Ciudad de Lanús"},
    {"nombre": "Banfield", "pais": "🇦🇷", "estadio": "Estadio Florencio Solá"},
    {"nombre": "Godoy Cruz", "pais": "🇦🇷", "estadio": "Estadio Feliciano Gambarte"},
    {"nombre": "Santos FC", "pais": "🇧🇷", "estadio": "Vila Belmiro"},
    {"nombre": "Fluminense", "pais": "🇧🇷", "estadio": "Maracanã"},
    {"nombre": "Athletico Paranaense", "pais": "🇧🇷", "estadio": "Arena da Baixada"},
    {"nombre": "Botafogo", "pais": "🇧🇷", "estadio": "Estádio Nilton Santos"},
    {"nombre": "Real Sociedad", "pais": "🇪🇸", "estadio": "Anoeta"},
    {"nombre": "Real Betis", "pais": "🇪🇸", "estadio": "Benito Villamarín"},
    {"nombre": "CA Osasuna", "pais": "🇪🇸", "estadio": "El Sadar"},
    {"nombre": "Crystal Palace", "pais": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "estadio": "Selhurst Park"},
    {"nombre": "Brighton & Hove Albion", "pais": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "estadio": "Amex Stadium"},
    {"nombre": "Brentford FC", "pais": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "estadio": "Gtech Community Stadium"},
    {"nombre": "Fulham FC", "pais": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "estadio": "Craven Cottage"},
    {"nombre": "Mainz 05", "pais": "🇩🇪", "estadio": "Mewa Arena"},
    {"nombre": "FC Augsburg", "pais": "🇩🇪", "estadio": "WWK Arena"},
    {"nombre": "Werder Bremen", "pais": "🇩🇪", "estadio": "Wohninvest Weserstadion"},
    {"nombre": "VfB Stuttgart", "pais": "🇩🇪", "estadio": "MHPArena"},
    {"nombre": "Lille OSC", "pais": "🇫🇷", "estadio": "Stade Pierre-Mauroy"},
    {"nombre": "Stade Rennais", "pais": "🇫🇷", "estadio": "Roazhon Park"},
    {"nombre": "OGC Nice", "pais": "🇫🇷", "estadio": "Allianz Riviera"},
    {"nombre": "Montpellier HSC", "pais": "🇫🇷", "estadio": "Stade de la Mosson"},
    {"nombre": "US Sassuolo", "pais": "🇮🇹", "estadio": "Mapei Stadium"},
    {"nombre": "Empoli FC", "pais": "🇮🇹", "estadio": "Stadio Carlo Castellani"},
    {"nombre": "Cagliari Calcio", "pais": "🇮🇹", "estadio": "Unipol Domus"},
    {"nombre": "Lecce", "pais": "🇮🇹", "estadio": "Stadio Via del Mare"},
    {"nombre": "Nacional", "pais": "🇺🇾", "estadio": "Gran Parque Central"},
    {"nombre": "Peñarol", "pais": "🇺🇾", "estadio": "Estadio Campeón del Siglo"},
    {"nombre": "Defensor Sporting", "pais": "🇺🇾", "estadio": "Estadio Luis Franzini"},
    {"nombre": "Atlético Nacional", "pais": "🇨🇴", "estadio": "Estadio Atanasio Girardot"},
    {"nombre": "Millonarios FC", "pais": "🇨🇴", "estadio": "El Campín"},
    {"nombre": "Junior de Barranquilla", "pais": "🇨🇴", "estadio": "Metropolitano"},
    {"nombre": "América de Cali", "pais": "🇨🇴", "estadio": "Estadio Olímpico Pascual Guerrero"},
    {"nombre": "Colo-Colo", "pais": "🇨🇱", "estadio": "Estadio Monumental"},
    {"nombre": "Universidad de Chile", "pais": "🇨🇱", "estadio": "Estadio Nacional"},
    {"nombre": "Cruz Azul", "pais": "🇲🇽", "estadio": "Estadio Azteca"},
    {"nombre": "Pachuca", "pais": "🇲🇽", "estadio": "Estadio Hidalgo"},
    {"nombre": "LDU Quito", "pais": "🇪🇨", "estadio": "Estadio Rodrigo Paz Delgado"},
    {"nombre": "Independiente del Valle", "pais": "🇪🇨", "estadio": "Estadio Banco Guayaquil"},
    {"nombre": "Barcelona SC", "pais": "🇪🇨", "estadio": "Estadio Monumental"},
    {"nombre": "Universitario", "pais": "🇵🇪", "estadio": "Estadio Monumental U"},
    {"nombre": "Sporting Cristal", "pais": "🇵🇪", "estadio": "Estadio Alberto Gallardo"},
    {"nombre": "Alianza Lima", "pais": "🇵🇪", "estadio": "Estadio Alejandro Villanueva"},
    {"nombre": "LA Galaxy", "pais": "🇺🇸", "estadio": "Dignity Health Sports Park"},
    {"nombre": "Atlanta United", "pais": "🇺🇸", "estadio": "Mercedes-Benz Stadium"},
    {"nombre": "Seattle Sounders", "pais": "🇺🇸", "estadio": "Lumen Field"},
]

def _init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        data = {"clubes": CLUBES_POR_DEFECTO}
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def _read_db():
    _init_db()
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _write_db(data):
    _init_db()
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR DB] No se pudo guardar la base de datos: {e}")

def get_user(user_id):
    user_id = str(user_id)
    db = _read_db()
    if user_id not in db:
        db[user_id] = {
            "monedas": 1000,
            "equipo": [],
            "puntos": 0,
            "victorias": 0,
            "derrotas": 0,
            "ultimo_entrenamiento": 0.0,
            "jugador": None,
            "club_actual": None,
            "convocado_seleccion": False,
            "partidos_jugados": 0,
            "goles": 0,
            "experiencia": 0.0,
            "ultimo_diario": 0.0,
            "diario_racha": 0,
            "insignias": [],
            "items": [],
            "racha_penales": 0,
            "ultimo_partido": 0.0,
            "proteccion_puntos": False,
            "racha_victorias": 0,
            "subastas_ganadas": 0,
            "historial_partidos": [],
            "temporada": 1,
            "skin_estadio": None,
            "train_boost": 0
        }
        _write_db(db)
    
    user_data = db[user_id]
    defaults = {
        "monedas": 1000,
        "equipo": [],
        "puntos": 0,
        "victorias": 0,
        "derrotas": 0,
        "ultimo_entrenamiento": 0.0,
        "jugador": None,
        "club_actual": None,
        "convocado_seleccion": False,
        "partidos_jugados": 0,
        "goles": 0,
        "experiencia": 0.0,
        "ultimo_diario": 0.0,
        "diario_racha": 0,
        "insignias": [],
        "items": [],
        "racha_penales": 0,
        "ultimo_partido": 0.0,
        "proteccion_puntos": False,
        "racha_victorias": 0,
        "subastas_ganadas": 0,
        "historial_partidos": [],
        "temporada": 1,
        "skin_estadio": None,
        "train_boost": 0
    }
    updated = False
    for k, v in defaults.items():
        if k not in user_data:
            user_data[k] = v
            updated = True
    if updated:
        _write_db(db)
        
    return user_data

def update_user(user_id, **kwargs):
    user_id = str(user_id)
    db = _read_db()
    # Inicializar si no existe
    if user_id not in db:
        get_user(user_id)
        db = _read_db()
        
    for k, v in kwargs.items():
        db[user_id][k] = v
    _write_db(db)

def get_saldo(user_id):
    return get_user(user_id)["monedas"]

def add_saldo(user_id, amount):
    user_id = str(user_id)
    data = get_user(user_id)
    new_saldo = data["monedas"] + amount
    update_user(user_id, monedas=new_saldo)
    return new_saldo

def sub_saldo(user_id, amount):
    user_id = str(user_id)
    data = get_user(user_id)
    new_saldo = max(0, data["monedas"] - amount)
    update_user(user_id, monedas=new_saldo)
    return new_saldo

def add_jugador(user_id, jugador):
    user_id = str(user_id)
    data = get_user(user_id)
    equipo = data.get("equipo", [])
    equipo.append(jugador)
    update_user(user_id, equipo=equipo)

def get_leaderboard(limit=10):
    db = _read_db()
    leaderboard = []
    for uid, stats in db.items():
        if uid == "clubes":
            continue
        leaderboard.append({
            "id": uid,
            "puntos": stats.get("puntos", 0),
            "victorias": stats.get("victorias", 0),
            "derrotas": stats.get("derrotas", 0)
        })
    leaderboard.sort(key=lambda x: x["puntos"], reverse=True)
    return leaderboard[:limit]

def get_leaderboard_rico(limit=10):
    db = _read_db()
    leaderboard = []
    for uid, stats in db.items():
        if uid == "clubes":
            continue
        leaderboard.append({
            "id": uid,
            "monedas": stats.get("monedas", 1000)
        })
    leaderboard.sort(key=lambda x: x["monedas"], reverse=True)
    return leaderboard[:limit]

def get_saldo_medio():
    db = _read_db()
    total = 0
    count = 0
    for uid, stats in db.items():
        if uid == "clubes":
            continue
        total += stats.get("monedas", 1000)
        count += 1
    return total // count if count > 0 else 1000

def add_insignia(user_id, insignia_id):
    user_id = str(user_id)
    data = get_user(user_id)
    insignias = data.get("insignias", [])
    if insignia_id not in insignias:
        insignias.append(insignia_id)
        update_user(user_id, insignias=insignias)
        recompensa = INSIGNIAS_RECOMPENSAS.get(insignia_id, 0)
        if recompensa > 0:
            add_saldo(user_id, recompensa)
        return True, recompensa
    return False, 0

def add_item(user_id, item_id):
    user_id = str(user_id)
    data = get_user(user_id)
    items = data.get("items", [])
    items.append(item_id)
    update_user(user_id, items=items)
    return True

def tiene_item(user_id, item_id):
    data = get_user(user_id)
    items = data.get("items", [])
    return item_id in items

def remove_item(user_id, item_id):
    user_id = str(user_id)
    data = get_user(user_id)
    items = data.get("items", [])
    if item_id in items:
        items.remove(item_id)
        update_user(user_id, items=items)
        return True
    return False

def seed_clubes():
    db = _read_db()
    if "clubes" not in db or not db["clubes"]:
        db["clubes"] = CLUBES_POR_DEFECTO
        _write_db(db)

def get_clubes():
    seed_clubes()
    return _read_db().get("clubes", [])

def add_club(club_data):
    db = _read_db()
    clubes = db.get("clubes", [])
    clubes.append(club_data)
    db["clubes"] = clubes
    _write_db(db)

def get_clubes_por_pais(pais_flag):
    return [c for c in get_clubes() if c["pais"] == pais_flag]

INSIGNIAS_RECOMPENSAS = {
    "primera_victoria": 100,
    "invicto_5": 300,
    "ascenso_d1": 500,
    "coleccionista": 200,
    "goleador": 300,
    "millonario": 1000,
    "racha_diaria_7": 400,
    "subasta_rey": 400
}

def add_insignia_with_reward(user_id, insignia_id):
    data = get_user(user_id)
    if insignia_id in data.get("insignias", []):
        return False, 0
    if add_insignia(user_id, insignia_id):
        recompensa = INSIGNIAS_RECOMPENSAS.get(insignia_id, 0)
        if recompensa > 0:
            add_saldo(user_id, recompensa)
        return True, recompensa
    return False, 0

def add_match_history(user_id, entry):
    user_id = str(user_id)
    data = get_user(user_id)
    historial = data.get("historial_partidos", [])
    historial.append(entry)
    if len(historial) > 50:
        historial = historial[-50:]
    update_user(user_id, historial_partidos=historial)

def get_predicciones_db():
    db = _read_db()
    return db.get("predicciones", {})

def save_prediccion(pid, data):
    db = _read_db()
    preds = db.get("predicciones", {})
    preds[pid] = data
    db["predicciones"] = preds
    _write_db(db)

def remove_prediccion(pid):
    db = _read_db()
    preds = db.get("predicciones", {})
    if pid in preds:
        del preds[pid]
        db["predicciones"] = preds
        _write_db(db)
