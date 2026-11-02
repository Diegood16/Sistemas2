# Configuracion general del proyecto 2
# Parametros de red para MQTT, datos de los bots de Telegram y rutas locales

import os
import socket
from pathlib import Path

# Directorio base del proyecto
directorio_proyecto = Path(__file__).resolve().parent.parent
carpeta_reportes = directorio_proyecto / 'reportes'
carpeta_reportes.mkdir(parents=True, exist_ok=True)

# Cargador automatico de variables desde archivo .env si existe
for ruta_env in [directorio_proyecto / '.env', Path(__file__).resolve().parent / '.env']:
    if ruta_env.exists():
        try:
            with open(ruta_env, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith('#') and '=' in linea:
                        clave, valor = linea.split('=', 1)
                        os.environ.setdefault(clave.strip(), valor.strip().strip('"\''))
        except Exception:
            pass

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
# Se pueden configurar via .env, variables de entorno o modificando este diccionario
# Si se define TELEGRAM_TOKEN_DEFAULT o TELEGRAM_CHAT_ID_DEFAULT, se usara como fallback
token_por_defecto = os.environ.get('TELEGRAM_TOKEN_DEFAULT', os.environ.get('TELEGRAM_TOKEN', ''))
chat_id_por_defecto = os.environ.get('TELEGRAM_CHAT_ID_DEFAULT', os.environ.get('TELEGRAM_CHAT_ID', ''))

bots = {
    1: {
        'nombre': 'Bot 1 - Material Particulado PM1.0',
        'token': os.environ.get('BOT_1_TOKEN', token_por_defecto) or 'TOKEN_BOT_1',
        'chat_id': os.environ.get('BOT_1_CHAT_ID', chat_id_por_defecto) or 'CHAT_ID_1',
    },
    2: {
        'nombre': 'Bot 2 - Material Particulado PM2.5',
        'token': os.environ.get('BOT_2_TOKEN', token_por_defecto) or 'TOKEN_BOT_2',
        'chat_id': os.environ.get('BOT_2_CHAT_ID', chat_id_por_defecto) or 'CHAT_ID_2',
    },
    3: {
        'nombre': 'Bot 3 - Material Particulado PM10',
        'token': os.environ.get('BOT_3_TOKEN', token_por_defecto) or 'TOKEN_BOT_3',
        'chat_id': os.environ.get('BOT_3_CHAT_ID', chat_id_por_defecto) or 'CHAT_ID_3',
    },
    4: {
        'nombre': 'Bot 4 - Medio Ambiente (Temp y HR)',
        'token': os.environ.get('BOT_4_TOKEN', token_por_defecto) or 'TOKEN_BOT_4',
        'chat_id': os.environ.get('BOT_4_CHAT_ID', chat_id_por_defecto) or 'CHAT_ID_4',
    },
}

def es_modo_simulado(token):
    # Si el token es de prueba o esta vacio, devolvemos True para operar en modo simulado
    # y evitar que el programa se caiga si aun no se configuran los bots reales en Telegram
    if not token or not isinstance(token, str):
        return True
    token_limpio = token.strip()
    if token_limpio == '' or token_limpio.startswith('TOKEN_BOT_') or 'YOUR_TOKEN' in token_limpio.upper():
        return True
    return False

def broker_esta_activo(host=broker_host, puerto=broker_puerto, tiempo_espera=1.0):
    # Verifica si el puerto del broker MQTT ya esta abierto y escuchando
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(tiempo_espera)
        try:
            return s.connect_ex((host, puerto)) == 0
        except Exception:
            return False
