# Publicador MQTT de mediciones de sensores simulados
# Emite datos de material particulado y medio ambiente segun la pauta

import sys
import time
import random
from pathlib import Path

# Aseguramos que el directorio actual este en el path para importar config
directorio_actual = Path(__file__).resolve().parent
if str(directorio_actual) not in sys.path:
    sys.path.insert(0, str(directorio_actual))

import paho.mqtt.publish as publish
from config import broker_host, broker_puerto, topico_particulas, topico_clima

def obtener_datos_particulas():
    # Genera lecturas de particulas segun los rangos del laboratorio:
    # mp01: 4 a 10 um, mp25: 10 a 50 um, mp10: 10 a 50 um
    mp01 = random.randint(4, 10)
    mp25 = random.randint(10, 50)
    mp10 = random.randint(10, 50)
    return f"{mp01},{mp25},{mp10}\n"

def obtener_datos_clima():
    # Genera lecturas ambientales segun los rangos de la guia:
    # temperatura: 10 a 22 °C, humedad relativa: 60 a 85 %
    temperatura = random.randint(10, 22)
    humedad = random.randint(60, 85)
    return f"{temperatura},{humedad}\n"

def main():
    print("[Publicador] Iniciando transmision de datos al broker MQTT...")
    print(f"[Publicador] Broker destino: {broker_host}:{broker_puerto}")
    print("[Publicador] Intervalo de envio: cada 5 segundos.")
    print("[Publicador] Presiona Ctrl+C para salir.\n")

    try:
        while True:
            # Seleccionamos al azar si toca transmitir datos de particulas o clima
            if random.choice([True, False]):
                topico = topico_particulas
                mensaje = obtener_datos_particulas()
            else:
                topico = topico_clima
                mensaje = obtener_datos_clima()

            # Publicamos el mensaje en el broker local
            publish.single(
                topic=topico,
                payload=mensaje,
                hostname=broker_host,
                port=broker_puerto
            )

            # Mostramos en consola el envio en formato limpio
            print(f"[Publicador] Enviado a {topico}: {mensaje.strip()}")

            # Pausa de 5 segundos segun la especificacion
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n[Publicador] Transmision detenida con Ctrl+C.")

if __name__ == '__main__':
    main()
