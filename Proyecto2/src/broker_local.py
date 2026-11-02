# Servidor Broker MQTT local usando amqtt
# Permite levantar un broker rapido en localhost sin instalar Mosquitto externo

import sys
import asyncio
import logging
from pathlib import Path

# Aseguramos que el directorio actual este en el path para importar config
directorio_actual = Path(__file__).resolve().parent
if str(directorio_actual) not in sys.path:
    sys.path.insert(0, str(directorio_actual))

from amqtt.broker import Broker
from config import broker_host, broker_puerto

# Configuramos logging de amqtt para advertencias unicamente
logging.basicConfig(level=logging.WARNING)

configuracion_broker = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': f'{broker_host}:{broker_puerto}',
        }
    },
    'sys_interval': 0,
    'auth': {
        'allow-anonymous': True,
    }
}

async def iniciar_broker():
    broker = Broker(configuracion_broker)
    await broker.start()
    print(f"[Broker] Servidor MQTT activo escuchando en {broker_host}:{broker_puerto}")
    print("[Broker] Esperando conexiones de publicadores y suscriptores...")
    print("[Broker] Presiona Ctrl+C para detener el servicio.\n")
    
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        print("\n[Broker] Deteniendo el servidor MQTT...")
        await broker.shutdown()
        print("[Broker] Servidor detenido exitosamente.")

def main():
    try:
        asyncio.run(iniciar_broker())
    except KeyboardInterrupt:
        print("\n[Broker] Proceso interrumpido con Ctrl+C. Cerrando broker.")

if __name__ == '__main__':
    main()
