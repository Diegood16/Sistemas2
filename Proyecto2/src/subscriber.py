# Modulo base de suscriptor MQTT, graficos y Telegram
# Cliente suscriptor que acumula 10 muestras, genera el reporte y lo manda a Telegram

import sys
import time
import threading
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Candado para que los hilos no se pisen al generar graficos con matplotlib
bloqueo_grafico = threading.Lock()

# Agregamos la ruta base para importar la configuracion
directorio_actual = Path(__file__).resolve().parent
if str(directorio_actual) not in sys.path:
    sys.path.insert(0, str(directorio_actual))

import paho.mqtt.client as mqtt

try:
    import telepot
except ImportError:
    telepot = None

from config import (
    broker_host,
    broker_puerto,
    topico_particulas,
    topico_clima,
    carpeta_reportes,
    bots
)

class ClienteSuscriptor:
    def __init__(self, cliente_id):
        # Guardamos el id del cliente (1, 2, 3 o 4)
        self.cliente_id = cliente_id
        
        # Obtenemos los datos del bot asignado segun la config
        datos_bot = bots.get(cliente_id, {
            'nombre': f'Bot {cliente_id}',
            'token': '',
            'chat_id': ''
        })
        })
        self.nombre_bot = datos_bot['nombre']
        self.token_bot = datos_bot['token']
        self.chat_id = datos_bot['chat_id']

        # Listas para almacenar las 10 muestras requeridas
        self.historial_mp01 = []
        self.historial_mp25 = []
        self.historial_mp10 = []
        self.historial_temp = []
        self.historial_hum = []

        # Contador de reportes generados
        self.contador_reportes = 0

        # Configuramos el cliente MQTT con soporte tanto para paho v2 como v1
        nombre_cliente_mqtt = f"cliente_suscriptor_{self.cliente_id}"
        try:
            self.cliente = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id=nombre_cliente_mqtt
            )
        except AttributeError:
            self.cliente = mqtt.Client(client_id=nombre_cliente_mqtt)

        # Asignamos los callbacks
        self.cliente.on_connect = self.on_connect
        self.cliente.on_message = self.on_message

    def on_connect(self, cliente, userdata, flags, codigo_respuesta, *args):
        # Comprobamos si la conexion fue exitosa
        es_exitoso = False
        if hasattr(codigo_respuesta, 'is_failure'):
            es_exitoso = not codigo_respuesta.is_failure
        elif codigo_respuesta == 0:
            es_exitoso = True

        if es_exitoso:
            print(f"[{self.nombre_bot}] Conectado al broker MQTT. Suscribiendose a topicos...")
            cliente.subscribe(topico_particulas)
            cliente.subscribe(topico_clima)
            print(f"[{self.nombre_bot}] Suscrito a '{topico_particulas}' y '{topico_clima}'. Esperando datos...")
        else:
            print(f"[{self.nombre_bot}] Error al conectar al broker. Codigo: {codigo_respuesta}")

    def on_message(self, cliente, userdata, mensaje):
        topico = mensaje.topic
        payload_texto = mensaje.payload.decode('utf-8').strip()

        try:
            # Procesamos lecturas de material particulado (MP 1.0, MP 2.5, MP 10)
            if topico == topico_particulas:
                valores = [int(v.strip()) for v in payload_texto.split(',') if v.strip()]
                if len(valores) == 3:
                    mp01, mp25, mp10 = valores
                    self.historial_mp01.append(mp01)
                    self.historial_mp25.append(mp25)
                    self.historial_mp10.append(mp10)

            # Procesamos lecturas ambientales (Temperatura y Humedad)
            elif topico == topico_clima:
                valores = [int(v.strip()) for v in payload_texto.split(',') if v.strip()]
                if len(valores) == 2:
                    temperatura, humedad = valores
                    self.historial_temp.append(temperatura)
                    self.historial_hum.append(humedad)

        except ValueError as error_conversion:
            print(f"[{self.nombre_bot}] Error al procesar datos de {topico}: {error_conversion}")
            return

        # Verificamos si completamos 10 muestras en ambos conjuntos de datos
        if len(self.historial_mp01) >= 10 and len(self.historial_temp) >= 10:
            hora_actual = time.strftime("%H:%M:%S")
            print(f"[{hora_actual}] [{self.nombre_bot}] Acumuladas 10 muestras. Generando reporte grafico...")
            
            # Tomamos exactamente las primeras 10 muestras
            muestras_mp01 = list(self.historial_mp01[:10])
            muestras_mp25 = list(self.historial_mp25[:10])
            muestras_mp10 = list(self.historial_mp10[:10])
            muestras_temp = list(self.historial_temp[:10])
            muestras_hum = list(self.historial_hum[:10])

            # Generamos el grafico y lo enviamos
            ruta_imagen = self.generar_grafico(
                muestras_mp01,
                muestras_mp25,
                muestras_mp10,
                muestras_temp,
                muestras_hum
            )
            self.enviar_telegram(ruta_imagen)

            # Limpiamos los primeros 10 elementos para no acumular indefinidamente pero conservar remanentes
            self.historial_mp01 = self.historial_mp01[10:]
            self.historial_mp25 = self.historial_mp25[10:]
            self.historial_mp10 = self.historial_mp10[10:]
            self.historial_temp = self.historial_temp[10:]
            self.historial_hum = self.historial_hum[10:]

    def generar_grafico(self, muestras_mp01, muestras_mp25, muestras_mp10, muestras_temp, muestras_hum):
        # Aumentamos el contador de reportes para nombrar el archivo
        self.contador_reportes += 1
        nombre_archivo = f"cliente_{self.cliente_id}_reporte_{self.contador_reportes}.png"
        ruta_imagen = carpeta_reportes / nombre_archivo

        # Candado adicional de concurrencia
        with bloqueo_grafico:
            # Usamos la API orientada a objetos de Matplotlib (Figure + FigureCanvasAgg)
            # para garantizar 100% thread-safety sin usar el singleton global de pyplot
            figura = Figure(figsize=(7.5, 7))
            canvas = FigureCanvasAgg(figura)
            ejes = figura.subplots(5, 1, sharex=True)
            figura.suptitle("Medicion MP1, MP2.5, MP10um - Tempe, HR", fontsize=12, y=0.98)

            # Los puntos corresponden a las 10 muestras (de 1 a 10)
            eje_x = list(range(1, 11))

            # Configuracion de cada subplot segun la especificacion exacta
            config_subplots = [
                (ejes[0], muestras_mp01, 'blue', 'ug/m3', 'MP01', (0, 50), [0, 10, 20, 30, 40, 50]),
                (ejes[1], muestras_mp25, 'green', 'ug/m3', 'MP25', (0, 50), [0, 10, 20, 30, 40, 50]),
                (ejes[2], muestras_mp10, 'red', 'ug/m3', 'MP10', (0, 50), [0, 10, 20, 30, 40, 50]),
                (ejes[3], muestras_temp, 'blue', 'Tempe', 'Tempe', (0, 50), [0, 10, 20, 30, 40, 50]),
                (ejes[4], muestras_hum, 'red', 'HR(%)', 'HR(%)', (50, 90), [50, 60, 70, 80, 90]),
            ]

            for ax, datos, color_linea, etiqueta_y, etiqueta_leyenda, limite_y, marcas_y in config_subplots:
                ax.plot(eje_x, datos, color=color_linea, label=etiqueta_leyenda, linewidth=1.2)
                ax.set_ylabel(etiqueta_y, fontsize=9)
                ax.set_ylim(limite_y)
                ax.set_yticks(marcas_y)
                ax.grid(True, linestyle=':', alpha=0.8)
                ax.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=9)

            # Configuracion del eje X inferior
            ejes[-1].set_xlabel("10 Samples Datas...", fontsize=10)
            ejes[-1].set_xlim(1, 13)
            ejes[-1].set_xticks([2, 4, 6, 8, 10, 12])

            # Ajustamos espaciado para que no se sobrepongan titulos ni valores
            figura.tight_layout()
            figura.subplots_adjust(top=0.93)

            # Guardamos la imagen directamente desde la figura y su canvas
            figura.savefig(ruta_imagen, dpi=150)

        return ruta_imagen

    def enviar_telegram(self, ruta_imagen):
        if not self.token_bot or not self.chat_id:
            print(f"[{self.nombre_bot}] Error: Token o Chat ID no configurados en el archivo .env.")
            return

        # Verificamos que telepot este instalado
        if telepot is None:
            print(f"[{self.nombre_bot}] Error: Libreria 'telepot' no instalada. No se pudo enviar el reporte.")
            return

        # Verificamos que la imagen exista y que este completamente escrita (mas de 20 KB)
        if not ruta_imagen.exists() or ruta_imagen.stat().st_size < 20000:
            print(f"[{self.nombre_bot}] Error: La imagen generada {ruta_imagen} esta vacia o corrupta.")
            return

        # Pequena pausa escalonada por cliente para no congestionar la conexion de Telegram
        time.sleep(0.3 * self.cliente_id)

        try:
            bot = telepot.Bot(self.token_bot)
            mensaje_caption = f"Reporte #{self.contador_reportes} - {self.nombre_bot}"
            with open(ruta_imagen, 'rb') as archivo_foto:
                bot.sendPhoto(self.chat_id, archivo_foto, caption=mensaje_caption)
            hora_actual = time.strftime("%H:%M:%S")
            print(f"[{hora_actual}] [{self.nombre_bot}] Reporte #{self.contador_reportes} enviado con exito a Telegram (Chat ID: {self.chat_id})")
        except Exception as error_telegram:
            # Atrapamos errores de conexion o token invalido para que el proceso no se caiga
            print(f"[{self.nombre_bot}] Error al enviar reporte por Telegram: {error_telegram}")

    def iniciar(self):
        # Inicia la conexion y el ciclo de escucha continuo de MQTT
        print(f"[{self.nombre_bot}] Conectando al broker MQTT en {broker_host}:{broker_puerto}...")
        self.cliente.connect(broker_host, broker_puerto, keepalive=60)
        self.cliente.loop_forever()

    def detener(self):
        # Detiene la conexion de manera ordenada
        self.cliente.disconnect()
        print(f"[{self.nombre_bot}] Cliente desconectado.")

def main():
    # Permitimos indicar el cliente_id por argumento (por defecto cliente 1)
    cliente_id = 1
    if len(sys.argv) > 1:
        try:
            cliente_id = int(sys.argv[1])
            if cliente_id not in (1, 2, 3, 4):
                print(f"Aviso: El cliente {cliente_id} no esta entre 1 y 4. Usando cliente 1 por defecto.")
                cliente_id = 1
        except ValueError:
            print("Parametro no valido, usando cliente 1.")
            cliente_id = 1

    suscriptor = ClienteSuscriptor(cliente_id=cliente_id)
    try:
        suscriptor.iniciar()
    except KeyboardInterrupt:
        print(f"\n[{suscriptor.nombre_bot}] Detenido con Ctrl+C.")
        suscriptor.detener()

if __name__ == '__main__':
    main()
