# Proyecto 2 - Simulador Completo (Todo en Uno)
# Ejecuta en paralelo el publicador de datos y los 4 clientes suscriptores
# Conecta directamente al broker Mosquitto en 127.0.0.1:1883 segun la pauta

import sys
import time
import random
import socket
import threading
from pathlib import Path

# Configuramos la ruta para importar modulos locales
directorio_actual = Path(__file__).resolve().parent
if str(directorio_actual) not in sys.path:
    sys.path.insert(0, str(directorio_actual))

import paho.mqtt.publish as publish
from config import broker_host, broker_puerto, topico_particulas, topico_clima
from subscriber import ClienteSuscriptor
from publicador import obtener_datos_particulas, obtener_datos_clima

# Evento global para coordinar el apagado ordenado de los hilos
evento_detener = threading.Event()

def verificar_broker_mosquitto():
    # Comprueba si el broker Mosquitto esta escuchando en el puerto 1883
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2.0)
        return s.connect_ex((broker_host, broker_puerto)) == 0

def tarea_publicador():
    # Espera 2 segundos para asegurar que los clientes esten suscritos
    evento_detener.wait(2.0)
    print("[Publicador] Publicador iniciado. Enviando datos a Mosquitto cada 5 segundos...\n")

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
                print(f"[Publicador] Error al publicar en Mosquitto: {error}")

        # Esperamos 5 segundos segun la pauta del profesor
        evento_detener.wait(5.0)

    print("[Publicador] Publicador detenido.")

def main():
    print("==========================================================")
    print("    SIMULADOR INTEGRADO PROYECTO 2 (MOSQUITTO + CLIENTES) ")
    print("==========================================================\n")

    # Verificamos que el broker Mosquitto este activo segun exige la pauta
    if not verificar_broker_mosquitto():
        print(f"[ERROR] No se pudo conectar al Broker Mosquitto en {broker_host}:{broker_puerto}.")
        print("Asegurate de que el servicio de Mosquitto este iniciado en Windows.")
        print("Puedes iniciarlo desde la consola de Windows con: net start mosquitto")
        print("\nPresiona Enter para salir...")
        input()
        return

    print(f"[OK] Broker Mosquitto detectado y activo en {broker_host}:{broker_puerto}.\n")

    # Inicializamos y arrancamos los 4 clientes suscriptores
    clientes = [ClienteSuscriptor(cliente_id=i) for i in range(1, 5)]
    hilos_suscriptores = []

    for cliente in clientes:
        hilo = threading.Thread(
            target=cliente.iniciar,
            name=f"Hilo-Cliente-{cliente.cliente_id}",
            daemon=True
        )
        hilo.start()
        hilos_suscriptores.append(hilo)

    # Pausa de 1.5 segundos para que los 4 clientes completen la suscripcion
    time.sleep(1.5)

    # Arrancamos el publicador
    hilo_pub = threading.Thread(target=tarea_publicador, name="Hilo-Publicador", daemon=True)
    hilo_pub.start()

    print("\nSistema completo en ejecucion. Presiona Ctrl+C para detener.\n")

    try:
        while not evento_detener.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[Simulador] Senal Ctrl+C recibida. Deteniendo clientes...")
        evento_detener.set()

        for cliente in clientes:
            try:
                cliente.detener()
            except Exception:
                pass

        for hilo in hilos_suscriptores:
            hilo.join(timeout=1.5)

        print("[Simulador] Sistema detenido con exito.")

if __name__ == '__main__':
    main()
