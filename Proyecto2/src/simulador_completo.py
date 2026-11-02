# Proyecto 2 - Simulador Completo (Todo en Uno)
# Ejecuta en paralelo el broker local, el publicador y los 4 suscriptores
# Permite probar toda la arquitectura sin tener que abrir varias terminales

import sys
import time
import random
import asyncio
import logging
import threading
from pathlib import Path

# Configuramos la ruta para importar modulos locales
directorio_actual = Path(__file__).resolve().parent
if str(directorio_actual) not in sys.path:
    sys.path.insert(0, str(directorio_actual))

import paho.mqtt.publish as publish
from amqtt.broker import Broker
from config import broker_host, broker_puerto, topico_particulas, topico_clima
from broker_local import configuracion_broker
from subscriber import ClienteSuscriptor
from publicador import obtener_datos_particulas, obtener_datos_clima

# Silenciamos mensajes verbosos de amqtt
logging.getLogger('amqtt').setLevel(logging.WARNING)

# Evento global para coordinar el apagado ordenado de todos los hilos
evento_detener = threading.Event()

def tarea_broker():
    # Revisamos si ya hay un broker corriendo en el puerto (como el servicio Mosquitto de Windows)
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ya_activo = (s.connect_ex((broker_host, broker_puerto)) == 0)

    if ya_activo:
        print(f"[Simulador] Broker MQTT detectado ya activo en {broker_host}:{broker_puerto} (Mosquitto). Usando broker existente.")
        return

    # Si no habia ninguno, levantamos el broker local en Python
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def correr():
        servidor_broker = Broker(configuracion_broker)
        await servidor_broker.start()
        print("[Simulador] Broker MQTT local iniciado en 127.0.0.1:1883")
        
        # Mantenemos vivo el broker mientras no se ordene detener
        while not evento_detener.is_set():
            await asyncio.sleep(0.3)
            
        print("[Simulador] Apagando Broker MQTT...")
        await servidor_broker.shutdown()
        print("[Simulador] Broker MQTT detenido.")

    try:
        loop.run_until_complete(correr())
    except Exception as error:
        if not evento_detener.is_set():
            print(f"[Simulador] Error en el broker local: {error}")
    finally:
        loop.close()

def tarea_publicador():
    # Esperamos 3 segundos iniciales para asegurar que broker y clientes esten listos
    evento_detener.wait(3.0)
    print("[Simulador] Publicador de datos iniciado. Enviando cada 5 segundos...")
    
    numero_envio = 1
    while not evento_detener.is_set():
        # Elegimos al azar si enviamos datos de particulas o clima
        if random.choice([True, False]):
            topico = topico_particulas
            mensaje = obtener_datos_particulas()
        else:
            topico = topico_clima
            mensaje = obtener_datos_clima()

        try:
            publish.single(
                topic=topico,
                payload=mensaje,
                hostname=broker_host,
                port=broker_puerto
            )
            print(f"[Publicador] Envio #{numero_envio} -> {topico}: {mensaje.strip()}")
            numero_envio += 1
        except Exception as error:
            if not evento_detener.is_set():
                print(f"[Publicador] Error al publicar datos: {error}")

        # Esperamos 5 segundos o despertamos antes si se presiono Ctrl+C
        evento_detener.wait(5.0)

    print("[Simulador] Publicador detenido.")

def main():
    print("Iniciando Simulador Completo de Proyecto 2...")
    print("Se levantaran el Broker local, los 4 Clientes y el Publicador.")
    print("Presiona Ctrl+C en cualquier momento para detener todo el sistema.\n")

    # 1. Levantamos el broker en un hilo de fondo
    hilo_broker = threading.Thread(target=tarea_broker, name="Hilo-Broker", daemon=True)
    hilo_broker.start()

    # Damos tiempo para que el broker este escuchando en el puerto 1883
    time.sleep(1.5)

    # 2. Inicializamos los 4 clientes suscriptores
    clientes = [ClienteSuscriptor(cliente_id=i) for i in range(1, 5)]
    hilos_suscriptores = []

    for cliente in clientes:
        hilo_cliente = threading.Thread(
            target=cliente.iniciar,
            name=f"Hilo-Cliente-{cliente.cliente_id}",
            daemon=True
        )
        hilo_cliente.start()
        hilos_suscriptores.append(hilo_cliente)

    # Damos un segundo para que los 4 clientes completen el handshake MQTT
    time.sleep(1.5)

    # 3. Levantamos el publicador en su propio hilo
    hilo_publicador = threading.Thread(target=tarea_publicador, name="Hilo-Publicador", daemon=True)
    hilo_publicador.start()

    print("\nSistema completo corriendo. Esperando datos y generando reportes...")

    # Bucle principal para escuchar la interrupcion del usuario (Ctrl+C)
    try:
        while not evento_detener.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[Simulador] Senal Ctrl+C recibida. Deteniendo servicios de forma ordenada...")
        evento_detener.set()

        # Detenemos primero la conexion MQTT de los clientes
        for cliente in clientes:
            try:
                cliente.detener()
            except Exception:
                pass

        # Esperamos que los hilos finalicen
        for hilo in hilos_suscriptores:
            hilo.join(timeout=2.0)

        hilo_publicador.join(timeout=2.0)
        hilo_broker.join(timeout=3.0)

        print("[Simulador] Todos los componentes detenidos. Simulacion finalizada con exito.")

if __name__ == '__main__':
    main()
