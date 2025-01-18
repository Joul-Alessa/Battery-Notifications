import signal
import sys

def handle_interrupt(signal_received, frame):
    print("Programa interrumpido. Realizando limpieza...")
    # Aquí puedes realizar tareas como cerrar archivos, guardar datos, etc.
    sys.exit(0)  # Salir del programa después de realizar la acción deseada

# Configuramos el manejador para la señal SIGINT
signal.signal(signal.SIGINT, handle_interrupt)

print("Presiona Ctrl+C para interrumpir el programa.")
try:
    while True:
        # Simulamos que el programa está en ejecución
        pass
except KeyboardInterrupt:
    # Esto no se usará porque ya interceptamos la señal SIGINT arriba.
    pass
