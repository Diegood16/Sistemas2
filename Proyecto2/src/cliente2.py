# Proyecto 2 - Cliente Suscriptor 2 (Material Particulado PM2.5)
# Escucha los topicos MQTT, acumula 10 muestras y genera el grafico para Telegram

import sys
from pathlib import Path

# Aseguramos que la carpeta src este en el path para importar
directorio_actual = Path(__file__).resolve().parent
if str(directorio_actual) not in sys.path:
    sys.path.insert(0, str(directorio_actual))

from subscriber import ClienteSuscriptor

def main():
    # Instanciamos el cliente 2 correspondiente a PM2.5
    suscriptor = ClienteSuscriptor(cliente_id=2)
    print("Iniciando Cliente Suscriptor 2 (PM2.5)...")
    print("Presiona Ctrl+C para detener.\n")

    try:
        suscriptor.iniciar()
    except KeyboardInterrupt:
        print("\nDeteniendo Cliente 2 con Ctrl+C...")
        suscriptor.detener()
        print("Cliente 2 finalizado con exito.")

if __name__ == '__main__':
    main()
