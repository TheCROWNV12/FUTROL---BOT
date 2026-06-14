# cogs/trivia.py
import discord
from discord.ext import commands
from discord import app_commands
import random
from utils import db

PREGUNTAS = [
    {"p": "¿Quién es el máximo goleador histórico de la Champions League?", "opciones": ["Lionel Messi", "Cristiano Ronaldo", "Raúl González", "Robert Lewandowski"], "r": "Cristiano Ronaldo"},
    {"p": "¿Cuántas Champions League tiene el Real Madrid?", "opciones": ["12", "14", "15", "10"], "r": "15"},
    {"p": "¿Qué jugador tiene el récord de más Balones de Oro ganados?", "opciones": ["Cristiano Ronaldo", "Pelé", "Johan Cruyff", "Lionel Messi"], "r": "Lionel Messi"},
    {"p": "¿En qué país se jugó el Mundial de la FIFA del año 2014?", "opciones": ["Sudáfrica", "Brasil", "Alemania", "Rusia"], "r": "Brasil"},
    {"p": "¿Qué selección nacional ganó el Mundial de Sudáfrica 2010?", "opciones": ["Países Bajos", "Alemania", "España", "Brasil"], "r": "España"},
    {"p": "¿Quién es el máximo goleador histórico de la Selección Argentina?", "opciones": ["Gabriel Batistuta", "Diego Maradona", "Hernán Crespo", "Lionel Messi"], "r": "Lionel Messi"},
    {"p": "¿Cuál es el nombre del estadio principal del FC Barcelona?", "opciones": ["Santiago Bernabéu", "San Siro", "Camp Nou", "Metropolitano"], "r": "Camp Nou"},
    {"p": "¿Qué club inglés ha ganado más títulos de Champions League?", "opciones": ["Manchester United", "Chelsea", "Arsenal", "Liverpool"], "r": "Liverpool"},
    {"p": "¿Quién anotó el famoso e histórico gol apodado 'La Mano de Dios'?", "opciones": ["Pelé", "Diego Maradona", "Mario Kempes", "Zico"], "r": "Diego Maradona"},
    {"p": "¿En qué club debutó profesionalmente Cristiano Ronaldo?", "opciones": ["Manchester United", "Real Madrid", "Sporting de Lisboa", "Juventus"], "r": "Sporting de Lisboa"},
    {"p": "¿Qué país ganó la primera Copa del Mundo de la historia en 1930?", "opciones": ["Argentina", "Uruguay", "Brasil", "Italia"], "r": "Uruguay"},
    {"p": "¿Qué legendario delantero brasileño es conocido como 'El Fenómeno'?", "opciones": ["Ronaldinho", "Ronaldo Nazário", "Romário", "Rivaldo"], "r": "Ronaldo Nazário"},
    {"p": "¿Qué selección nacional ha ganado más Copas del Mundo?", "opciones": ["Alemania", "Italia", "Brasil", "Argentina"], "r": "Brasil"},
    {"p": "¿Qué equipo de la Premier League es conocido popularmente como 'Los Gunners'?", "opciones": ["Chelsea", "Arsenal", "Tottenham", "West Ham"], "r": "Arsenal"},
    {"p": "¿Quién era el director técnico del FC Barcelona durante el famoso sextete de 2009?", "opciones": ["Luis Enrique", "Pep Guardiola", "Frank Rijkaard", "Tito Vilanova"], "r": "Pep Guardiola"},
    {"p": "¿Qué país ganó la Eurocopa 2020 (disputada en el año 2021)?", "opciones": ["Inglaterra", "Francia", "España", "Italia"], "r": "Italia"},
    {"p": "¿Quién ganó el Balón de Oro en 2018 rompiendo la hegemonía de Messi y CR7?", "opciones": ["Luka Modrić", "Antoine Griezmann", "Neymar Jr", "Mohamed Salah"], "r": "Luka Modrić"},
    {"p": "¿Cómo se conoce popularmente al trofeo que gana el campeón de la liga italiana?", "opciones": ["La Liga", "Scudetto", "Copa Italia", "Coppa Nazionale"], "r": "Scudetto"},
    {"p": "¿Cuál es el nombre del estadio del Real Madrid?", "opciones": ["Wanda Metropolitano", "Mestalla", "San Mamés", "Santiago Bernabéu"], "r": "Santiago Bernabéu"},
    {"p": "¿Qué jugador de fútbol francés ganó el Balón de Oro en el año 2022?", "opciones": ["Kylian Mbappé", "Karim Benzema", "Antoine Griezmann", "Paul Pogba"], "r": "Karim Benzema"},
    {"p": "¿En qué mundial ocurrió el famoso cabezazo de Zidane a Materazzi?", "opciones": ["Corea-Japón 2002", "Alemania 2006", "Sudáfrica 2010", "Francia 1998"], "r": "Alemania 2006"},
    {"p": "¿Quién es el máximo goleador histórico de la Selección de Brasil?", "opciones": ["Pelé", "Ronaldo Nazário", "Neymar Jr", "Romário"], "r": "Neymar Jr"},
    {"p": "¿Qué club de la Bundesliga alemana disputa sus partidos como local en el Allianz Arena?", "opciones": ["Borussia Dortmund", "Bayer Leverkusen", "Bayern Múnich", "RB Leipzig"], "r": "Bayern Múnich"},
    {"p": "¿Cuántos minutos dura un partido reglamentario de fútbol sin prórroga?", "opciones": ["80 minutos", "90 minutos", "100 minutos", "120 minutos"], "r": "90 minutos"},
    {"p": "¿Qué histórico club italiano de la Serie A tiene el apodo de 'La Vecchia Signora'?", "opciones": ["AC Milan", "Inter de Milán", "Juventus", "AS Roma"], "r": "Juventus"},
    {"p": "¿Cuál es el clásico rival histórico de Boca Juniors en el fútbol argentino?", "opciones": ["Independiente", "Racing Club", "River Plate", "San Lorenzo"], "r": "River Plate"},
    {"p": "¿Qué jugador anotó el gol de la victoria en la final de la Champions League 2021 (Chelsea vs Man City)?", "opciones": ["Kai Havertz", "N'Golo Kanté", "Mason Mount", "Timo Werner"], "r": "Kai Havertz"},
    {"p": "¿Qué selección africana sorprendió al mundo llegando a semifinales en Qatar 2022?", "opciones": ["Camerún", "Senegal", "Ghana", "Marruecos"], "r": "Marruecos"},
    {"p": "¿Quién es el máximo goleador histórico de todos los Mundiales de la FIFA?", "opciones": ["Pelé", "Miroslav Klose", "Ronaldo Nazário", "Just Fontaine"], "r": "Miroslav Klose"},
    {"p": "¿Qué club italiano de fútbol posee más títulos de Champions League?", "opciones": ["Juventus", "Inter de Milán", "AC Milan", "AS Roma"], "r": "AC Milan"},
    {"p": "¿Qué legendario astro argentino del fútbol es conocido como 'El Pelusa'?", "opciones": ["Lionel Messi", "Diego Maradona", "Mario Kempes", "Alfredo Di Stéfano"], "r": "Diego Maradona"},
    {"p": "¿Qué selección nacional europea es apodada 'La Naranja Mecánica'?", "opciones": ["Alemania", "Bélgica", "Países Bajos", "Dinamarca"], "r": "Países Bajos"},
    {"p": "¿Qué país organizará el Mundial de 2026 junto a Estados Unidos y Canadá?", "opciones": ["México", "Costa Rica", "Colombia", "Panamá"], "r": "México"},
    {"p": "¿Quién es el máximo goleador histórico de la Premier League inglesa?", "opciones": ["Wayne Rooney", "Alan Shearer", "Harry Kane", "Thierry Henry"], "r": "Alan Shearer"},
    {"p": "¿Qué equipo ganó la final de la Copa Libertadores 2018 disputada en el Santiago Bernabéu?", "opciones": ["Boca Juniors", "River Plate", "Flamengo", "Gremio"], "r": "River Plate"},
    {"p": "¿A qué club europeo fue traspasado Neymar Jr procedente del Santos FC de Brasil?", "opciones": ["Real Madrid", "Paris Saint-Germain", "FC Barcelona", "Chelsea"], "r": "FC Barcelona"},
    {"p": "¿Qué jugador belga es considerado el cerebro del mediocampo del Manchester City?", "opciones": ["Eden Hazard", "Romelu Lukaku", "Kevin De Bruyne", "Youri Tielemans"], "r": "Kevin De Bruyne"},
    {"p": "¿En qué país se inventaron las reglas modernas del fútbol?", "opciones": ["Brasil", "Inglaterra", "Francia", "Italia"], "r": "Inglaterra"},
    {"p": "¿Quién ganó el Balón de Oro en el año 2007 antes del inicio de la era Messi/Ronaldo?", "opciones": ["Ronaldinho", "Thierry Henry", "Kaká", "Zinedine Zidane"], "r": "Kaká"},
    {"p": "¿Qué arquero español fue el guante de oro y figura en el Mundial 2010?", "opciones": ["Victor Valdés", "Iker Casillas", "Pepe Reina", "David de Gea"], "r": "Iker Casillas"},
    {"p": "¿Cuál es el apodo oficial de los aficionados y del club Atlético de Madrid?", "opciones": ["Merengues", "Culés", "Colchoneros", "Palanganas"], "r": "Colchoneros"},
    {"p": "¿Qué país sudamericano ganó la Copa América del año 2021?", "opciones": ["Brasil", "Argentina", "Colombia", "Chile"], "r": "Argentina"},
    {"p": "¿Qué club francés ha dominado casi por completo la Ligue 1 en la última década?", "opciones": ["AS Mónaco", "Lille OSC", "Olympique de Lyon", "Paris Saint-Germain"], "r": "Paris Saint-Germain"},
    {"p": "¿Quién es el máximo goleador histórico de la selección masculina de Inglaterra?", "opciones": ["Wayne Rooney", "Harry Kane", "Bobby Charlton", "Gary Lineker"], "r": "Harry Kane"},
    {"p": "¿En qué estadio se disputó la gran final de la Copa del Mundo Qatar 2022?", "opciones": ["Estadio Al Bayt", "Estadio de Lusail", "Estadio 974", "Estadio Jalifa"], "r": "Estadio de Lusail"},
    {"p": "¿Qué país ganó la Eurocopa de Francia en el año 2016?", "opciones": ["Francia", "Portugal", "Alemania", "Gales"], "r": "Portugal"},
    {"p": "¿Qué club español de fútbol es conocido como el 'Submarino Amarillo'?", "opciones": ["Villarreal CF", "Cádiz CF", "UD Las Palmas", "Real Betis"], "r": "Villarreal CF"},
    {"p": "¿En qué año se fundó el organismo internacional del fútbol (FIFA)?", "opciones": ["1898", "1904", "1914", "1930"], "r": "1904"},
    {"p": "¿Qué delantero alemán es apodado 'Der Bomber' por su gran cantidad de goles?", "opciones": ["Miroslav Klose", "Jürgen Klinsmann", "Gerd Müller", "Karl-Heinz Rummenigge"], "r": "Gerd Müller"},
    {"p": "¿Qué habilidoso jugador argentino es conocido en el mundo del fútbol como 'El Fideo'?", "opciones": ["Sergio Agüero", "Ángel Di María", "Lautaro Martínez", "Paulo Dybala"], "r": "Ángel Di María"},
    {"p": "¿Qué histórico club inglés de fútbol juega sus partidos como local en Old Trafford?", "opciones": ["Manchester City", "Liverpool FC", "Arsenal FC", "Manchester United"], "r": "Manchester United"},
    {"p": "¿Qué club inglés de fútbol se coronó campeón de la Champions League de 2019?", "opciones": ["Tottenham Hotspur", "Chelsea", "Liverpool FC", "Manchester City"], "r": "Liverpool FC"},
    {"p": "¿En qué club de fútbol europeo se retiró profesionalmente Zinedine Zidane?", "opciones": ["Juventus FC", "Real Madrid", "Girondins de Burdeos", "AS Cannes"], "r": "Real Madrid"},
    {"p": "¿Quién ostenta el récord de más asistencias oficiales en la historia del fútbol?", "opciones": ["Thomas Müller", "Neymar Jr", "Lionel Messi", "Kevin De Bruyne"], "r": "Lionel Messi"},
    {"p": "¿Cuál es la distancia reglamentaria en metros desde el punto de penal hasta la línea de gol?", "opciones": ["9.15 metros", "11 metros", "12 metros", "10 metros"], "r": "11 metros"},
    {"p": "¿Qué equipo alemán es el clásico rival del Bayern Múnich en 'Der Klassiker'?", "opciones": ["Schalke 04", "Borussia Dortmund", "Bayer Leverkusen", "Werder Bremen"], "r": "Borussia Dortmund"},
    {"p": "¿Qué delantero uruguayo de élite es apodado 'El Pistolero'?", "opciones": ["Edinson Cavani", "Diego Forlán", "Luis Suárez", "Darwin Núñez"], "r": "Luis Suárez"},
    {"p": "¿Quién es el máximo goleador histórico de la selección de Francia masculina?", "opciones": ["Thierry Henry", "Kylian Mbappé", "Olivier Giroud", "Michel Platini"], "r": "Olivier Giroud"},
    {"p": "¿En qué club francés debutó profesionalmente el delantero Kylian Mbappé?", "opciones": ["Paris Saint-Germain", "AS Mónaco", "Olympique de Marsella", "LOSC Lille"], "r": "AS Mónaco"},
    {"p": "¿Qué país ganó el Mundial de 1954 en el histórico suceso apodado 'El Milagro de Berna'?", "opciones": ["Hungría", "Alemania Federal", "Suiza", "Austria"], "r": "Alemania Federal"},
    {"p": "¿Qué club inglés logró el triplete continental (Premier, FA Cup y UCL) en el año 2023?", "opciones": ["Manchester United", "Liverpool FC", "Chelsea FC", "Manchester City"], "r": "Manchester City"},
    {"p": "¿Quién ganó el primer Balón de Oro otorgado en toda la historia (1956)?", "opciones": ["Alfredo Di Stéfano", "Pelé", "Stanley Matthews", "Raymond Kopa"], "r": "Stanley Matthews"},
    {"p": "¿Qué selección nacional de Sudamérica tiene como apodo oficial 'La Celeste'?", "opciones": ["Argentina", "Uruguay", "Paraguay", "Chile"], "r": "Uruguay"},
    {"p": "¿De qué famosa cantera portuguesa salió la estrella Cristiano Ronaldo?", "opciones": ["SL Benfica", "FC Porto", "Sporting de Lisboa", "Braga"], "r": "Sporting de Lisboa"},
    {"p": "¿Cuál es el estadio principal del Liverpool FC inglés?", "opciones": ["Old Trafford", "Etihad Stadium", "Anfield", "Goodison Park"], "r": "Anfield"},
    {"p": "¿Qué club italiano de fútbol comparte el Estadio Olímpico de Roma con la Lazio?", "opciones": ["AC Milan", "Juventus FC", "Napoli", "AS Roma"], "r": "AS Roma"},
    {"p": "¿Qué director técnico tiene el récord de más títulos de Champions League ganados?", "opciones": ["Pep Guardiola", "Carlo Ancelotti", "Alex Ferguson", "Zinedine Zidane"], "r": "Carlo Ancelotti"},
    {"p": "¿Qué país asiático coorganizó la Copa del Mundo de la FIFA en 2002 junto con Japón?", "opciones": ["China", "Corea del Sur", "Catar", "Arabia Saudita"], "r": "Corea del Sur"},
    {"p": "¿Qué club holandés de gran tradición europea ha ganado 4 Champions League?", "opciones": ["PSV Eindhoven", "Feyenoord", "Ajax de Ámsterdam", "AZ Alkmaar"], "r": "Ajax de Ámsterdam"},
    {"p": "¿Cuál es la nacionalidad de origen del gran goleador Robert Lewandowski?", "opciones": ["Alemana", "Ucraniana", "Checa", "Polaca"], "r": "Polaca"},
    {"p": "¿Qué club londinense tiene en su escudo un gallo de pelea y es apodado 'Spurs'?", "opciones": ["Chelsea", "West Ham", "Arsenal", "Tottenham Hotspur"], "r": "Tottenham Hotspur"},
    {"p": "¿En qué ciudad española se encuentra ubicado el Estadio de Mestalla?", "opciones": ["Sevilla", "Barcelona", "Madrid", "Valencia"], "r": "Valencia"},
    {"p": "¿Qué jugador posee el récord de más partidos disputados en Copas del Mundo?", "opciones": ["Lothar Matthäus", "Lionel Messi", "Miroslav Klose", "Cristiano Ronaldo"], "r": "Lionel Messi"},
    {"p": "¿Qué selección de Sudamérica es apodada habitualmente 'La Tri'?", "opciones": ["Colombia", "Venezuela", "Ecuador", "Bolivia"], "r": "Ecuador"},
    {"p": "¿Qué selección de Concacaf es la máxima ganadora de Copas Oro de la historia?", "opciones": ["Estados Unidos", "Canadá", "Costa Rica", "México"], "r": "México"},
    {"p": "¿Qué club italiano viste tradicionalmente de azul y negro con rayas verticales?", "opciones": ["AC Milan", "Atalanta", "Inter de Milán", "Sampdoria"], "r": "Inter de Milán"},
    {"p": "¿En qué club de los Estados Unidos juega Lionel Messi a partir de 2023?", "opciones": ["LA Galaxy", "Inter Miami", "New York Red Bulls", "LAFC"], "r": "Inter Miami"},
    {"p": "¿Qué club de fútbol de Escocia sostiene la mítica rivalidad de la 'Old Firm' contra Rangers?", "opciones": ["Hearts", "Aberdeen", "Celtic FC", "Hibernian"], "r": "Celtic FC"},
    {"p": "¿Qué delantero brasileño anotó el doblete de la victoria para Flamengo en la final de Libertadores 2019?", "opciones": ["Bruno Henrique", "Gabriel Barbosa (Gabigol)", "Everton Ribeiro", "De Arrascaeta"], "r": "Gabriel Barbosa (Gabigol)"},
    {"p": "¿Qué portero italiano fue campeón en 2006 y es catalogado leyenda de la Juventus?", "opciones": ["Gianluigi Buffon", "Francesco Toldo", "Gianluca Pagliuca", "Walter Zenga"], "r": "Gianluigi Buffon"},
    {"p": "¿Qué centrocampista español fue el socio de Iniesta en el Barça y ahora es DT?", "opciones": ["Xabi Alonso", "Xavi Hernández", "Sergio Busquets", "Cesc Fàbregas"], "r": "Xavi Hernández"},
    {"p": "¿Qué apodo recibe la selección nacional masculina de Japón?", "opciones": ["Dragones Rojos", "Tigres de Asia", "Guerreros Taeguk", "Samuráis Azules"], "r": "Samuráis Azules"},
    {"p": "¿Qué selección de Centroamérica logró la hazaña de llegar a cuartos de final en Brasil 2014?", "opciones": ["Honduras", "Costa Rica", "Panamá", "El Salvador"], "r": "Costa Rica"},
    {"p": "¿Cómo es denominado comercial y popularmente el clásico entre Real Madrid y FC Barcelona?", "opciones": ["El Derbi", "El Clásico", "El Súper Clásico", "El Gran Partido"], "r": "El Clásico"},
    {"p": "¿En qué país sudamericano se encuentra situado el legendario Estadio de Maracaná?", "opciones": ["Argentina", "Uruguay", "Colombia", "Brasil"], "r": "Brasil"},
    {"p": "¿Qué club del fútbol argentino es apodado con orgullo 'El Xeneize'?", "opciones": ["River Plate", "Boca Juniors", "Racing Club", "San Lorenzo de Almagro"], "r": "Boca Juniors"},
    {"p": "¿Qué equipo inglés es recordado por terminar una Premier League completa invicto (2003-2004)?", "opciones": ["Manchester United", "Chelsea FC", "Arsenal FC", "Liverpool FC"], "r": "Arsenal FC"},
    {"p": "¿Qué jugador galés anotó una espectacular chilena en la final de Champions League de 2018?", "opciones": ["Ryan Giggs", "Gareth Bale", "Aaron Ramsey", "Daniel James"], "r": "Gareth Bale"},
    {"p": "¿Qué club de la Ligue 1 de Francia es conocido por su lema 'Droit au but' y ganó la UCL en 1993?", "opciones": ["Paris Saint-Germain", "AS Mónaco", "Olympique de Lyon", "Olympique de Marsella"], "r": "Olympique de Marsella"},
    {"p": "¿Qué carismático delantero sueco ha jugado en Ajax, Juventus, Inter, Barça, Milan, PSG y Man United?", "opciones": ["Henrik Larsson", "Zlatan Ibrahimović", "Marcus Berg", "Emil Forsberg"], "r": "Zlatan Ibrahimović"},
    {"p": "¿Qué selección africana es apodada popularmente 'Las Estrellas Negras'?", "opciones": ["Nigeria", "Camerún", "Costa de Marfil", "Ghana"], "r": "Ghana"},
    {"p": "¿Quién era el director técnico de la Selección de Argentina en el Mundial México 1986?", "opciones": ["César Luis Menotti", "Carlos Bilardo", "Alfio Basile", "Daniel Passarella"], "r": "Carlos Bilardo"},
    {"p": "¿Quién es el máximo goleador histórico de la selección italiana de fútbol?", "opciones": ["Roberto Baggio", "Luigi Riva", "Alessandro Del Piero", "Francesco Totti"], "r": "Luigi Riva"},
    {"p": "¿Qué club alemán de la Bundesliga es de propiedad de la empresa de bebidas energéticas Red Bull?", "opciones": ["Bayer Leverkusen", "RB Leipzig", "Hoffenheim", "Wolfsburgo"], "r": "RB Leipzig"},
    {"p": "¿En qué edición del Mundial de fútbol de la FIFA se introdujo por primera vez el uso de las tarjetas amarilla y roja?", "opciones": ["Inglaterra 1966", "México 1970", "Alemania 1974", "España 1982"], "r": "México 1970"},
    {"p": "¿Cuál es la duración del tiempo extra o prórroga total (dividido en dos tiempos) en fase eliminatoria?", "opciones": ["20 minutos", "30 minutos", "40 minutos", "15 minutos"], "r": "30 minutos"},
    {"p": "¿Qué selección nacional caribeña hizo su debut histórico en un Mundial en Alemania 2006?", "opciones": ["Jamaica", "Trinidad y Tobago", "Haití", "Cuba"], "r": "Trinidad y Tobago"},
    {"p": "¿Qué jugador apodado 'El Principito' fue campeón con Francia y es estandarte del Atlético de Madrid?", "opciones": ["Karim Benzema", "Paul Pogba", "Antoine Griezmann", "Hugo Lloris"], "r": "Antoine Griezmann"},
    {"p": "¿Qué club del fútbol de Portugal es conocido por sus aficionados como 'Los Dragones'?", "opciones": ["Sporting de Lisboa", "SL Benfica", "FC Porto", "Braga"], "r": "FC Porto"},
    {"p": "¿Cuántas Copas América tiene Argentina?", "opciones": ["14", "15", "16", "17"], "r": "16"},
    {"p": "¿Qué jugador tiene el récord de más goles en un año calendario (2012)?", "opciones": ["Cristiano Ronaldo", "Lionel Messi", "Robert Lewandowski", "Pelé"], "r": "Lionel Messi"},
    {"p": "¿Qué selección ganó la primera Eurocopa en 1960?", "opciones": ["Francia", "Unión Soviética", "España", "Italia"], "r": "Unión Soviética"},
    {"p": "¿Cuántos Mundiales tiene la Selección Argentina?", "opciones": ["2", "3", "4", "1"], "r": "3"},
    {"p": "¿Qué estadio es conocido como 'La Bombonera'?", "opciones": ["Estadio Monumental", "Estadio Alberto J. Armando", "Estadio Libertadores de América", "Estadio Presidente Perón"], "r": "Estadio Alberto J. Armando"},
    {"p": "¿Qué jugador argentino es conocido como 'El Cuti'?", "opciones": ["Nicolás Otamendi", "Germán Pezzella", "Cristian Romero", "Lisandro Martínez"], "r": "Cristian Romero"},
    {"p": "¿Cuántos Balones de Oro tiene Lionel Messi?", "opciones": ["7", "8", "6", "9"], "r": "8"},
    {"p": "¿Qué selección africana ganó más Copas Africanas?", "opciones": ["Nigeria", "Egipto", "Camerún", "Ghana"], "r": "Egipto"},
    {"p": "¿En qué año se fundó el FC Barcelona?", "opciones": ["1899", "1902", "1898", "1900"], "r": "1899"},
    {"p": "¿Qué equipo ganó la Premier League 2015-16 de forma sorprendente?", "opciones": ["Leicester City", "Tottenham", "Arsenal", "Southampton"], "r": "Leicester City"},
    {"p": "¿Cuántos goles hizo Messi en la final del Mundial 2022?", "opciones": ["1", "2", "3", "0"], "r": "2"},
    {"p": "¿Qué entrenador es conocido como 'El Bigote' y ganó la Champions con el Liverpool?", "opciones": ["Jürgen Klopp", "Rafa Benítez", "Bob Paisley", "Bill Shankly"], "r": "Rafa Benítez"},
    {"p": "¿Qué país tiene más Copas América?", "opciones": ["Brasil", "Argentina", "Uruguay", "Chile"], "r": "Argentina"},
    {"p": "¿Cuál es el récord de asistencia en un Mundial?", "opciones": ["Maracaná 1950", "Estadio Azteca 1970", "Camp Nou 1982", "Lusail 2022"], "r": "Maracaná 1950"},
    {"p": "¿Qué club brasileño tiene más Libertadores?", "opciones": ["Santos", "Flamengo", "São Paulo", "Gremio"], "r": "Flamengo"},
    {"p": "¿Quién es el máximo goleador en la historia de la Copa Libertadores?", "opciones": ["Pelé", "Alberto Spencer", "Zico", "Messi"], "r": "Alberto Spencer"},
    {"p": "¿Cuántos equipos participan en el Mundial desde 1998?", "opciones": ["24", "32", "48", "16"], "r": "32"},
    {"p": "¿Qué selección ganó la Copa Confederaciones más veces?", "opciones": ["Brasil", "Francia", "España", "Alemania"], "r": "Brasil"},
    {"p": "¿Qué jugador es conocido como 'La Saeta Rubia'?", "opciones": ["Luis Suárez Miramontes", "Alfredo Di Stéfano", "Ferenc Puskás", "Eusébio"], "r": "Alfredo Di Stéfano"},
    {"p": "¿Qué estadio albergó la final del Mundial 1978?", "opciones": ["Estadio Monumental", "Estadio Mario Kempes", "Estadio José Amalfitani", "Estadio Gigante de Arroyito"], "r": "Estadio Monumental"},
    {"p": "¿Cuál es el club con más Champions League de la historia?", "opciones": ["AC Milan", "Liverpool", "Bayern Múnich", "Real Madrid"], "r": "Real Madrid"},
    {"p": "¿Qué jugador anotó el gol 1000 de la historia de los Mundiales?", "opciones": ["Maradona", "Pelé", "Messi", "Ronaldo"], "r": "Pelé"},
    {"p": "¿En qué estadio juega la Juventus desde 2011?", "opciones": ["San Siro", "Estadio Olímpico de Roma", "Allianz Stadium", "Estadio delle Alpi"], "r": "Allianz Stadium"},
    {"p": "¿Qué selección asiática ganó más Copas Asiáticas?", "opciones": ["Japón", "Corea del Sur", "Arabia Saudita", "Irán"], "r": "Japón"},
    {"p": "¿Quién ganó la Bota de Oro en el Mundial 2022?", "opciones": ["Lionel Messi", "Kylian Mbappé", "Julián Álvarez", "Olivier Giroud"], "r": "Kylian Mbappé"},
    {"p": "¿Cuál es el nombre oficial del estadio del Inter Miami?", "opciones": ["DRV PNK Stadium", "Chase Stadium", "Inter Miami Stadium", "Freedom Park"], "r": "Chase Stadium"},
    {"p": "¿Qué club ganó la primera edición de la Premier League en 1992-93?", "opciones": ["Manchester United", "Blackburn Rovers", "Arsenal", "Leeds United"], "r": "Manchester United"},
    {"p": "¿Cuál es el país con más Mundiales femeninos?", "opciones": ["Estados Unidos", "Alemania", "Noruega", "Japón"], "r": "Estados Unidos"},
    {"p": "¿Qué jugador es conocido como 'El Matador'?", "opciones": ["Luis Suárez", "Edinson Cavani", "Radamel Falcao", "Mario Kempes"], "r": "Radamel Falcao"},
    {"p": "¿Quién fue el primer Balón de Oro de la historia?", "opciones": ["Alfredo Di Stéfano", "Stanley Matthews", "Raymond Kopa", "Pelé"], "r": "Stanley Matthews"},
    {"p": "¿Qué portero tiene más partidos invicto en Champions?", "opciones": ["Iker Casillas", "Gianluigi Buffon", "Manuel Neuer", "Petr Čech"], "r": "Iker Casillas"},
    {"p": "¿Qué selección ganó la Eurocopa 1992 de forma sorpresiva?", "opciones": ["Suecia", "Dinamarca", "Países Bajos", "Alemania"], "r": "Dinamarca"},
    {"p": "¿Cuál es el estadio más grande de Europa?", "opciones": ["Camp Nou", "Wembley", "Santiago Bernabéu", "Signal Iduna Park"], "r": "Camp Nou"},
    {"p": "¿Cuántas Copas del Mundo tiene Alemania?", "opciones": ["3", "4", "5", "2"], "r": "4"},
    {"p": "¿Qué club argentino tiene más Copas Libertadores?", "opciones": ["Boca Juniors", "River Plate", "Independiente", "Estudiantes"], "r": "Independiente"},
    {"p": "¿Qué delantero inglés es conocido como 'El Niño Maravilla'?", "opciones": ["Michael Owen", "Wayne Rooney", "Harry Kane", "Raheem Sterling"], "r": "Michael Owen"},
    {"p": "¿En qué año se jugó el primer Mundial femenino?", "opciones": ["1991", "1995", "1999", "1987"], "r": "1991"},
    {"p": "¿Qué jugador brasileño ganó 3 Mundiales (1958, 62, 70)?", "opciones": ["Pelé", "Garrincha", "Rivelino", "Zagallo"], "r": "Pelé"},
    {"p": "¿Cuál es el club de fútbol más antiguo de Argentina?", "opciones": ["Boca Juniors", "River Plate", "Gimnasia LP", "Quilmes"], "r": "Gimnasia LP"},
    {"p": "¿Qué selección ganó la Copa Oro 2023?", "opciones": ["Estados Unidos", "México", "Panamá", "Canadá"], "r": "México"},
    {"p": "¿Cuántos minutos de descuento hubo en la final del Mundial 2022?", "opciones": ["8", "10", "6", "12"], "r": "8"},
    {"p": "¿Qué atacante galés es conocido como 'El Expreso de Gales'?", "opciones": ["Gareth Bale", "Ryan Giggs", "Aaron Ramsey", "John Hartson"], "r": "Gareth Bale"},
    {"p": "¿Cuál es la ciudad del club Borussia Dortmund?", "opciones": ["Berlín", "Dortmund", "Múnich", "Hamburgo"], "r": "Dortmund"},
    {"p": "¿Qué jugador tiene más asistencias en la historia de Champions?", "opciones": ["Cristiano Ronaldo", "Lionel Messi", "Kevin De Bruyne", "Xavi Hernández"], "r": "Cristiano Ronaldo"},
    {"p": "¿Qué selección ganó el primer Mundial de la FIFA en 1930?", "opciones": ["Argentina", "Uruguay", "Brasil", "Estados Unidos"], "r": "Uruguay"},
    {"p": "¿Qué club ganó la Champions League 2012 en penales contra Bayern?", "opciones": ["Chelsea", "Manchester United", "Arsenal", "Tottenham"], "r": "Chelsea"},
    {"p": "¿Qué entrenador argentino dirigió al Barcelona en la era del sextete?", "opciones": ["Diego Maradona", "Pep Guardiola", "Jorge Valdano", "Marcelo Bielsa"], "r": "Pep Guardiola"},
    {"p": "¿Cuál es el apodo de la selección de Austria?", "opciones": ["La Naranja Mecánica", "El Equipo", "Das Team", "Los Diablos Rojos"], "r": "Das Team"},
    {"p": "¿Qué club colombiano es conocido como 'Los Embajadores'?", "opciones": ["Millonarios", "Atlético Nacional", "América de Cali", "Junior"], "r": "Millonarios"},
    {"p": "¿Cuántas Copas América ganó Chile en su historia?", "opciones": ["2", "3", "1", "4"], "r": "2"},
    {"p": "¿Qué delantero es el máximo goleador histórico de la Bundesliga?", "opciones": ["Gerd Müller", "Robert Lewandowski", "Klaus Fischer", "Jupp Heynckes"], "r": "Gerd Müller"},
    {"p": "¿En qué estadio juega el AC Milan?", "opciones": ["San Siro", "Allianz Stadium", "Estadio Olímpico de Roma", "Artemio Franchi"], "r": "San Siro"},
    {"p": "¿Qué país ganó el Mundial Sub-20 más veces?", "opciones": ["Brasil", "Argentina", "España", "Portugal"], "r": "Argentina"},
    {"p": "¿Qué jugador es conocido como 'Duracell' por su incansable recorrido?", "opciones": ["N'Golo Kanté", "Park Ji-sung", "Daniele De Rossi", "Gennaro Gattuso"], "r": "N'Golo Kanté"},
    {"p": "¿Qué club francés tiene más Ligas 1?", "opciones": ["Paris Saint-Germain", "Saint-Étienne", "Olympique de Marsella", "Olympique de Lyon"], "r": "Paris Saint-Germain"},
    {"p": "¿Cuál es la mascota del Mundial 2026?", "opciones": ["Fuleco", "Goleo VI", "La'eeb", "TBA"], "r": "TBA"},
    {"p": "¿Qué jugador tiene más partidos en la historia de La Liga?", "opciones": ["Xavi Hernández", "Andoni Zubizarreta", "Raúl", "Iker Casillas"], "r": "Andoni Zubizarreta"},
    {"p": "¿Qué selección de Oceanía ha participado más veces en Mundiales?", "opciones": ["Australia", "Nueva Zelanda", "Tahití", "Fiyi"], "r": "Australia"},
    {"p": "¿Cuántos goles lleva Messi vs Cristiano en enfrentamientos directos?", "opciones": ["Messi lidera", "CR7 lidera", "Están igualados", "Nunca se enfrentaron"], "r": "Messi lidera"},
    {"p": "¿Qué entrenador portugués es conocido como 'El Mago'?", "opciones": ["José Mourinho", "André Villas-Boas", "Fernando Santos", "Vítor Pereira"], "r": "José Mourinho"},
    {"p": "¿Qué club peruano tiene más títulos nacionales?", "opciones": ["Universitario", "Alianza Lima", "Sporting Cristal", "Melgar"], "r": "Universitario"},
    {"p": "¿Qué jugador belga fue Balón de Oro en 2018?", "opciones": ["Eden Hazard", "Kevin De Bruyne", "Luka Modrić", "Thibaut Courtois"], "r": "Luka Modrić"},
    {"p": "¿Cuántos Mundiales ha organizado México?", "opciones": ["2", "3", "1", "4"], "r": "3"},
    {"p": "¿Qué selección es apodada 'Los Cafeteros'?", "opciones": ["Colombia", "Costa Rica", "México", "Ecuador"], "r": "Colombia"},
    {"p": "¿Qué portero ganó el Balón de Oro en 1963?", "opciones": ["Lev Yashín", "Gianluigi Buffon", "Dino Zoff", "Iker Casillas"], "r": "Lev Yashín"},
    {"p": "¿Cuál es el equipo de fútbol más antiguo de España?", "opciones": ["FC Barcelona", "Real Madrid", "Athletic Club", "Recreativo de Huelva"], "r": "Recreativo de Huelva"},
    {"p": "¿Qué selección caribeña participó en el Mundial 1998?", "opciones": ["Cuba", "Jamaica", "Haití", "Trinidad y Tobago"], "r": "Jamaica"},
    {"p": "¿Cuántas veces ganó el Real Madrid la Champions en el siglo XXI?", "opciones": ["5", "7", "6", "8"], "r": "7"},
    {"p": "¿Qué jugador es conocido como 'El Cholo' aparte del DT?", "opciones": ["Diego Simeone", "Antoine Griezmann", "João Félix", "Ángel Correa"], "r": "Diego Simeone"},
    {"p": "¿Qué país ganó la Copa América 2024?", "opciones": ["Argentina", "Brasil", "Uruguay", "Colombia"], "r": "Argentina"},
    {"p": "¿En qué año se inventó el VAR en el fútbol profesional?", "opciones": ["2016", "2018", "2014", "2020"], "r": "2016"},
    {"p": "¿Qué estadio es conocido como 'El Coloso del Parque'?", "opciones": ["Estadio Monumental", "La Bombonera", "El Cilindro", "Estadio Jorge Luis Hirschi"], "r": "Estadio Monumental"},
    {"p": "¿Qué equipo brasileño tiene el apodo 'Timão'?", "opciones": ["Corinthians", "Palmeiras", "Santos", "São Paulo"], "r": "Corinthians"},
    {"p": "¿Quién inventó el 'Fútbol Total'?", "opciones": ["Rinus Michels", "Johan Cruyff", "Arrigo Sacchi", "Valeriy Lobanovskyi"], "r": "Rinus Michels"},
    {"p": "¿Cuál es el récord de goles en una temporada de La Liga?", "opciones": ["50 goles (Messi)", "48 goles (Messi)", "46 goles (Messi)", "44 goles (CR7)"], "r": "50 goles (Messi)"},
    {"p": "¿Qué club ecuatoriano tiene más títulos de LigaPro?", "opciones": ["Barcelona SC", "LDU Quito", "Emelec", "El Nacional"], "r": "Barcelona SC"},
    {"p": "¿Qué selección africana debutó en un Mundial en 2018?", "opciones": ["Senegal", "Panamá", "Islandia", "Túnez"], "r": "Panamá"},
    {"p": "¿Cuál es el país de origen de Luis Figo?", "opciones": ["España", "Portugal", "Brasil", "Francia"], "r": "Portugal"},
    {"p": "¿Qué club ganó la Copa Sudamericana 2023?", "opciones": ["Defensa y Justicia", "LDU Quito", "Fortaleza", "Independiente del Valle"], "r": "LDU Quito"},
    {"p": "¿Cuántos Mundiales disputó Cristiano Ronaldo hasta 2026?", "opciones": ["5", "6", "4", "7"], "r": "6"},
    {"p": "¿Qué arquero es conocido como 'San Iker'?", "opciones": ["Iker Casillas", "David de Gea", "Víctor Valdés", "Keylor Navas"], "r": "Iker Casillas"},
    {"p": "¿Cuál es la liga nacional más vista del mundo?", "opciones": ["Premier League", "La Liga", "Bundesliga", "Serie A"], "r": "Premier League"},
    {"p": "¿Qué club uruguayo tiene más títulos de Liga?", "opciones": ["Nacional", "Peñarol", "Defensor Sporting", "Danubio"], "r": "Peñarol"},
    {"p": "¿Qué jugador alemán es conocido como 'El Kaiser'?", "opciones": ["Franz Beckenbauer", "Gerd Müller", "Lothar Matthäus", "Karl-Heinz Rummenigge"], "r": "Franz Beckenbauer"},
    {"p": "¿Cuántas Ligas de Campeones tiene el FC Barcelona?", "opciones": ["5", "6", "4", "7"], "r": "5"},
    {"p": "¿Qué técnica se usa para medir fuera de juego con tecnología?", "opciones": ["VAR", "SAOT", "GLT", "Semi-automated offside"], "r": "Semi-automated offside"},
    {"p": "¿Qué club inglés ganó la Premier 2023-24?", "opciones": ["Manchester City", "Arsenal", "Liverpool", "Chelsea"], "r": "Manchester City"},
    {"p": "¿Qué selección es conocida como 'Los Leones Indomables'?", "opciones": ["Senegal", "Camerún", "Marruecos", "Nigeria"], "r": "Camerún"},
    {"p": "¿En qué año debutó Messi en el Barcelona?", "opciones": ["2003", "2004", "2005", "2002"], "r": "2004"},
    {"p": "¿Cuánto pesa aproximadamente un balón oficial de la FIFA?", "opciones": ["410-450g", "350-400g", "450-500g", "500-550g"], "r": "410-450g"},
    {"p": "¿Qué entrenador ganó la Premier con el Leicester City?", "opciones": ["Claudio Ranieri", "Brendan Rodgers", "Nigel Pearson", "Craig Shakespeare"], "r": "Claudio Ranieri"},
    {"p": "¿Qué país de Sudamérica nunca ganó la Copa América?", "opciones": ["Ecuador", "Venezuela", "Bolivia", "Paraguay"], "r": "Venezuela"},
    {"p": "¿Qué club portugués tiene el apodo 'Águias' (Águilas)?", "opciones": ["SL Benfica", "FC Porto", "Sporting CP", "Braga"], "r": "SL Benfica"},
    {"p": "¿Qué selección eliminó a Argentina en el Mundial 2018?", "opciones": ["Francia", "Croacia", "Inglaterra", "Brasil"], "r": "Francia"},
    {"p": "¿Cuál es el club con más títulos internacionales del mundo?", "opciones": ["Real Madrid", "Barcelona", "AC Milan", "Boca Juniors"], "r": "Real Madrid"},
    {"p": "¿En qué ciudad nació Lionel Messi?", "opciones": ["Buenos Aires", "Rosario", "Córdoba", "Santa Fe"], "r": "Rosario"},
    {"p": "¿Qué jugador tiene más títulos de Liga en la historia?", "opciones": ["Ryan Giggs", "Lionel Messi", "Paolo Maldini", "Xavi Hernández"], "r": "Ryan Giggs"},
    {"p": "¿Qué arquero tiene más penales atajados en la Champions?", "opciones": ["Manuel Neuer", "Gianluigi Buffon", "Iker Casillas", "Edwin van der Sar"], "r": "Iker Casillas"},
    {"p": "¿Cuántas finales de Champions perdió la Juventus?", "opciones": ["7", "5", "6", "8"], "r": "7"},
    {"p": "¿Qué selección centroamericana es apodada 'Los Ticos'?", "opciones": ["Costa Rica", "Honduras", "Panamá", "El Salvador"], "r": "Costa Rica"},
    {"p": "¿En qué año se introdujo la regla del gol de visitante en Europa?", "opciones": ["1965", "1970", "1958", "1980"], "r": "1965"},
    {"p": "¿Cuántos Mundiales de Clubes ganó el Real Madrid?", "opciones": ["5", "8", "7", "6"], "r": "8"},
    {"p": "¿Qué selección islandesa sorprendió en la Eurocopa 2016?", "opciones": ["Islandia", "Gales", "Irlanda del Norte", "Albania"], "r": "Islandia"},
]

class TriviaButtons(discord.ui.View):
    def __init__(self, author, pregunta, opciones, correct_ans, message=None):
        super().__init__(timeout=20)
        self.author = author
        self.pregunta = pregunta
        self.opciones = opciones
        self.correct_ans = correct_ans
        self.message = message

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        
        embed = discord.Embed(
            title="🧠 TRIVIA FUTBOLERA — TIEMPO AGOTADO",
            description=(
                "⏳ **¡Se acabó el tiempo!**\n"
                "Nadie logró responder esta pregunta dentro del límite.\n\n"
                f"🔍 La respuesta correcta era: **{self.correct_ans}**"
            ),
            color=0xE74C3C  # Rojo
        )
        embed.set_footer(text="FUTROL — Usa /trivia para intentarlo de nuevo")
        
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except Exception:
                pass
        self.stop()

    async def check_answer(self, interaction: discord.Interaction, selected_index: int):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ ¡Esta trivia no es tuya! Ejecuta `/trivia` para jugar la tuya propia.", ephemeral=True)
            return

        await interaction.response.defer()

        for child in self.children:
            child.disabled = True

        selected_option = self.opciones[selected_index]
        is_correct = selected_option == self.correct_ans

        if is_correct:
            recompensa = 100
            db.add_saldo(self.author.id, recompensa)
            color = 0x2ECC71  # Verde Esmeralda
            resultado = (
                "🎉 **¡RESPUESTA CORRECTA!** 🎉\n\n"
                f"👏 ¡Excelente conocimiento táctico, {self.author.mention}!\n\n"
                f"⭐ Recompensa: **+100 monedas** 💰"
            )
        else:
            color = 0xE74C3C  # Rojo
            resultado = (
                "❌ **¡RESPUESTA INCORRECTA!** ❌\n\n"
                f"🏃 Sigue entrenando la táctica, {self.author.mention}.\n\n"
                f"🔍 La respuesta correcta era: **{self.correct_ans}**"
            )

        nuevo_saldo = db.get_saldo(self.author.id)
        
        embed = discord.Embed(
            title="🧠 TRIVIA FUTBOLERA — RESULTADO",
            description=resultado,
            color=color
        )
        embed.add_field(name="❓ Pregunta", value=self.pregunta, inline=False)
        embed.add_field(name="💰 Saldo Actual", value=f"`{nuevo_saldo} monedas`", inline=False)
        embed.set_footer(text="FUTROL — El bot definitivo del fútbol ⚽")

        await interaction.edit_original_response(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="A 🇦", style=discord.ButtonStyle.primary, custom_id="trivia_a")
    async def opc_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 0)

    @discord.ui.button(label="B 🇧", style=discord.ButtonStyle.primary, custom_id="trivia_b")
    async def opc_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 1)

    @discord.ui.button(label="C 🇨", style=discord.ButtonStyle.primary, custom_id="trivia_c")
    async def opc_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 2)

    @discord.ui.button(label="D 🇩", style=discord.ButtonStyle.primary, custom_id="trivia_d")
    async def opc_d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 3)


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="trivia", description="🧠 Responde una pregunta de fútbol y gana 100 monedas")
    async def trivia(self, interaction: discord.Interaction):
        pregunta = random.choice(PREGUNTAS)
        opciones = list(pregunta["opciones"])
        random.shuffle(opciones)
        
        correct_answer = pregunta["r"]
        
        embed = discord.Embed(
            title="🧠 TRIVIA FUTBOLERA — FUTROL",
            description="Demuestra tu conocimiento del deporte rey. ¡Solo tienes 20 segundos para responder!",
            color=0x3498DB  # Azul Deportivo
        )
        embed.add_field(name="❓ Pregunta", value=f"**{pregunta['p']}**", inline=False)
        
        letras = ["🇦", "🇧", "🇨", "🇩"]
        texto_opciones = "\n".join([f"{letras[i]} **{opciones[i]}**" for i in range(len(opciones))])
        embed.add_field(name="📋 Opciones", value=texto_opciones, inline=False)
        embed.set_footer(text="Haz clic en el botón correspondiente abajo para responder • FUTROL")

        view = TriviaButtons(interaction.user, pregunta["p"], opciones, correct_answer)
        await interaction.response.send_message(embed=embed, view=view)
        
        view.message = await interaction.original_response()

async def setup(bot):
    await bot.add_cog(Trivia(bot))