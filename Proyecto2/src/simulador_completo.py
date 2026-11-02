# Proyecto 2 - Simulador Completo (Todo en Uno)
# Ejecuta en paralelo el broker (si no hay uno activo), el publicador y los 4 suscriptores
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
from config import (
    broker_host,
    broker_puerto,
    topico_particulas,
    topico_clima,
    intervalo_publicacion,
    broker_esta_activo
)
from broker_local import configuracion_broker
from subscriber import ClienteSuscriptor
from publicador import obtener_datos_particulas, obtener_datos_clima

# Silenciamos mensajes verbosos de amqtt
logging.getLogger('amqtt').setLevel(logging.WARNING)

# Evento global para coordinar el apagado ordenado de todos los hilos
evento_detener = threading.Event()
broker_iniciado_por_script = False

def tarea_broker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def correr():
        servidor_broker = Broker(configuracion_broker)
        await servidor_broker.start()
        print("[Simulador] Broker MQTT fallback iniciado en 127.0.0.1:1883")
        
        while not evento_detener.is_set():
            await asyncio.sleep(0.3)
            
        print("[Simulador] Apagando Broker MQTT fallback...")
        await servidor_broker.shutdown()
        print("[Simulador] Broker MQTT detenido.")

    try:
        loop.run_until_complete(correr())
    except Exception as error:
        if not evento_detener.is_set():
            print(f"[Simulador] Error inesperado en el broker fallback: {error}")
    finally:
        loop.close()

def tarea_publicador():
    evento_detener.wait(2.0)
    print(f"[Simulador] Publicador de datos iniciado. Enviando cada {intervalo_publicacion} segundos...")
    
    numero_envio = 1
    while not evento_detener.is_set():
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

        evento_detener.wait(intervalo_publicacion)

    print("[Simulador] Publicador detenido.")

def main():
    global broker_iniciado_por_script
    print("========================================================")
    print("       SIMULADOR COMPLETO - PROYECTO 2 (INFO1157)")
    print("========================================================")
    print("Presiona Ctrl+C en cualquier momento para detener todo.\n")

    hilo_broker = None
    if broker_esta_activo(broker_host, broker_puerto):
        print(f"[Simulador] Broker MQTT oficial (Mosquitto) detectado en {broker_host}:{broker_puerto}.")
        print("[Simulador] Conectando directamente al broker existente.")
    else:
        print(f"[Simulador] No se detecto broker en {broker_host}:{broker_puerto}.")
        print("[Simulador] Levantando broker local amqtt integrado...")
        broker_iniciado_por_script = True
        hilo_broker = threading.Thread(target=tarea_broker, name="Hilo-Broker", daemon=True)
        hilo_broker.start()
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

    time.sleep(1.5)

    # 3. Levantamos el publicador en su propio hilo
    hilo_publicador = threading.Thread(target=tarea_publicador, name="Hilo-Publicador", daemon=True)
    hilo_publicador.start()

    print("\nSistema completo corriendo. Esperando datos y generando reportes...")

    try:
        while not evento_detener.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[Simulador] Senal Ctrl+C recibida. Deteniendo servicios de forma ordenada...")
        evento_detener.set()

        for cliente in clientes:
            try:
                cliente.detener()
            except Exception:
                pass

        for hilo in hilos_suscriptores:
            hilo.join(timeout=2.0)

        hilo_publicador.join(timeout=2.0)
        if hilo_broker is not None:
            hilo_broker.join(timeout=3.0)

        print("[Simulador] Todos los componentes detenidos. Simulacion finalizada con exito.")

if __name__ == '__main__':
    main()
