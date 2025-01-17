# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 12:23:01 2025

@author: josel
"""

import psutil
import time
from notifypy import Notify

def check_battery_level():
    # Obtener información de la batería
    battery = psutil.sensors_battery()
    if battery is not None:
        level = battery.percent
        plugged = battery.power_plugged
        
        # Verificar el nivel de la batería y si está conectada a la corriente
        if level <= 20 and not plugged:
            #Envia notificacion de sistema
            notification = Notify()
            notification.title = "Alerta de Batería"
            notification.message = f"⚠️ Advertencia: Nivel de batería bajo ({level} %). \nConecta el cargador."
            notification.send()
            
            time.sleep(80)
        elif level >= 90 and plugged:
            #Envia notificacion de sistema
            notification = Notify()
            notification.title = "Alerta de Batería"
            notification.message = f"⚡ Batería casi llena ({level} %). \nConsidera desconectar el cargador."
            notification.send()
            
            time.sleep(80)
    else:
        print("No se pudo obtener información sobre la batería.")
        exit()

# ciclo para revisar el nivel de la batería
def main():
    while True:
        check_battery_level()
        time.sleep(10)  # Espera 10 segundos antes de volver a comprobar

if __name__ == "__main__":
    main()