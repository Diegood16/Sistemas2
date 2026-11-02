# Proyecto 2 - Cliente Suscriptor 3 (Material Particulado PM10)
# Escucha los topicos MQTT, acumula 10 muestras y genera el grafico para Telegram

import sys
from pathlib import Path

# Aseguramos que la carpeta src este en el path para importar
directorio_actual = Path(__file__).resolve().parent
if str(directorio_actual) not in sys.path:
    sys.path.insert(0, str(directorio_actual))

from subscriber import ClienteSuscriptor

def main():
    # Instanciamos el cliente 3 correspondiente a PM10
    suscriptor = ClienteSuscriptor(cliente_id=3)
    print("Iniciando Cliente Suscriptor 3 (PM10)...")
    print("Presiona Ctrl+C para detener.\n")

    try:
        suscriptor.iniciar()
    except KeyboardInterrupt:
        print("\nDeteniendo Cliente 3 con Ctrl+C...")
        suscriptor.detener()
        print("Cliente 3 finalizado con exito.")

if __name__ == '__main__':
    main()
