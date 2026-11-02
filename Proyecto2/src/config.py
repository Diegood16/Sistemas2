# Configuracion general del proyecto 2
# Parametros de red para MQTT, datos de los bots de Telegram y rutas locales

import os
from pathlib import Path

# Directorio base del proyecto y carpeta de reportes
directorio_proyecto = Path(__file__).resolve().parent.parent
carpeta_reportes = directorio_proyecto / 'reportes'
carpeta_reportes.mkdir(parents=True, exist_ok=True)

# Cargamos variables de entorno desde el archivo .env si existe (buscamos en Proyecto2 o en la raiz)
posibles_rutas_env = [
    directorio_proyecto / '.env',
    directorio_proyecto.parent / '.env',
    Path.cwd() / '.env'
]

for archivo_env in posibles_rutas_env:
    if archivo_env.exists():
        try:
            with open(archivo_env, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith('#') and '=' in linea:
                        clave, valor = linea.split('=', 1)
                        os.environ.setdefault(clave.strip(), valor.strip().strip('"\''))
            break
        except Exception as error_env:
            print(f"[Config] Error al leer archivo .env: {error_env}")

# Parametros de conexion para el Broker MQTT local
broker_host = os.environ.get('MQTT_BROKER_HOST', '127.0.0.1')
broker_puerto = int(os.environ.get('MQTT_BROKER_PORT', 1883))

# Topicos segun la especificacion del profesor
# DATA/MP -> Material Particulado (MP 1.0, MP 2.5, MP 10)
# DATA/MA -> Medio Ambiente (Temperatura, Humedad Relativa)
topico_particulas = 'DATA/MP'
topico_clima = 'DATA/MA'
topicos = [topico_particulas, topico_clima]

# Intervalo de publicacion de datos en segundos (por defecto 5 segundos segun pauta)
intervalo_publicacion = float(os.environ.get('INTERVALO_PUBLICACION', 5.0))

# Configuracion de los 4 bots de Telegram solicitados
# Carga directa de las credenciales reales desde .env
bots = {
    1: {
        'nombre': 'Bot 1 - Material Particulado PM1.0',
        'token': os.environ.get('BOT_1_TOKEN', ''),
        'chat_id': os.environ.get('BOT_1_CHAT_ID', ''),
    },
    2: {
        'nombre': 'Bot 2 - Material Particulado PM2.5',
        'token': os.environ.get('BOT_2_TOKEN', ''),
        'chat_id': os.environ.get('BOT_2_CHAT_ID', ''),
    },
    3: {
        'nombre': 'Bot 3 - Material Particulado PM10',
        'token': os.environ.get('BOT_3_TOKEN', ''),
        'chat_id': os.environ.get('BOT_3_CHAT_ID', ''),
    },
    4: {
        'nombre': 'Bot 4 - Medio Ambiente (Temp y HR)',
        'token': os.environ.get('BOT_4_TOKEN', ''),
        'chat_id': os.environ.get('BOT_4_CHAT_ID', ''),
    },
}
