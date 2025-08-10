'''
Esta versión funciona bien pero al cerrar la ventana, el proceso se muere
'''

import os
import json
import toga
import shutil
from playsound import playsound
import threading
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import socket
import io
import sys
from PIL import Image, ImageDraw
import pystray

def create_image():
    # Crea un icono básico para el tray
    image = Image.new('RGB', (64, 64), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill=(255, 255, 255))
    return image

class NotificationsApp(toga.App):
    def startup(self):
        # Obtener el directorio actual y verificar si carpeta sounds existe
        current_directory = os.path.dirname(os.path.abspath(__file__))
        sounds_directory = os.path.join(current_directory, 'sounds')

        if not os.path.exists(sounds_directory):
            os.makedirs(sounds_directory)
            print("Carpeta 'sounds' creada.")
        else:
            print("La carpeta 'sounds' ya existe.")
        
        # Leer valores desde conf.json
        try:
            with open("conf.json", "r") as f:
                config = json.load(f)
                default_min_json = str(config.get("lower", 0))
                default_max_json = str(config.get("higher", 100))
                default_sound_enabled_json = config.get("sound", False)
                default_closing_notif_json = config.get("closing", True)
                default_msg_telegram_json = config.get("msgTelegram", False)
                default_chat_id_telegram_json = config.get("chatIdTelegram", "")
                default_bot_id_telegram_json = config.get("botIdTelegram", "")
                default_sleep_time_json = config.get("sleepTime", "")
                default_port_json = config.get("port", "")
        except Exception as e:
            print("Error leyendo conf.json:", e)
            default_min_json = "0"
            default_max_json = "100"
            default_sound_enabled_json = False
            default_closing_notif_json = True
            default_msg_telegram_json = False
            default_chat_id_telegram_json = ""
            default_bot_id_telegram_json = ""
            default_sleep_time_json = "60"
            default_port_json = "1111"
        
        # Contenedor principal
        main_box = toga.Box(style=Pack(direction=COLUMN, margin=10))

        # Título 1
        title_1_label = toga.Label(
            "Battery Notifications",
            style=Pack(font_size=20, margin_bottom=20, text_align="center", alignment="center")
        )
        main_box.add(title_1_label)

        # Fila horizontal con los campos de notificaciones
        input_row_1 = toga.Box(
            style=Pack(direction=ROW, gap=10, flex=1, alignment="center", justify_content="center")
        )

        # Porcentaje mínimo
        min_percentage_label = toga.Label("Minimum (%):", style=Pack(width=90))
        self.min_percentage_input = toga.TextInput(
            value=default_min_json,
            on_change=self.validate_input,
            style=Pack(width=100)
        )

        # Porcentaje máximo
        max_percentage_label = toga.Label("Maximum (%):", style=Pack(width=90))
        self.max_percentage_input = toga.TextInput(
            value=default_max_json,
            on_change=self.validate_input,
            style=Pack(width=100)
        )

        # Agregar widgets a la fila
        input_row_1.add(min_percentage_label)
        input_row_1.add(self.min_percentage_input)
        input_row_1.add(max_percentage_label)
        input_row_1.add(self.max_percentage_input)

        # Envolver la fila en otro contenedor para centrarla
        centered_row_1_box = toga.Box(
            style=Pack(direction=ROW, justify_content="center")
        )
        centered_row_1_box.add(input_row_1)

        # Agregar fila a la ventana principal
        main_box.add(centered_row_1_box)

        # Título 2
        title_2_label = toga.Label(
            "Sound",
            style=Pack(font_size=20, margin_top=10, margin_bottom=20, text_align="center", alignment="center")
        )
        main_box.add(title_2_label)

        # Fila con Enable, low/high y botones select
        self.input_row_2 = toga.Box(
            style=Pack(direction=ROW, gap=10, flex=1, alignment="center", justify_content="center")
        )

        # Primer grupo: Enable + Switch (una fila horizontal)
        enable_group = toga.Box(style=Pack(direction=ROW, gap=10))
        enable_sounds_label = toga.Label("Enable sounds notifications:", style=Pack(padding=(5, 0)))
        self.enable_sounds_checkbox = toga.Switch(
            "",
            style=Pack(),
            on_change=self.toggle_sounds_fields,
            value=default_sound_enabled_json
        )
        enable_group.add(enable_sounds_label)
        enable_group.add(self.enable_sounds_checkbox)

        # Segundo grupo: bloque vertical con filas individuales para cada sonido
        self.sound_column = toga.Box(style=Pack(direction=COLUMN, gap=5))

        # Verifica y añade botones para reproducir sonidos existentes
        low_sound_path = os.path.join(sounds_directory, "battery-low.mp3")
        high_sound_path = os.path.join(sounds_directory, "battery-high.mp3")
        disconnect_sound_path = os.path.join(sounds_directory, "disconnect.mp3")

        # Fila: Low
        low_row = toga.Box(style=Pack(direction=ROW, gap=10))
        low_sound_label = toga.Label("Low battery sound:", style=Pack(padding=(5, 0)))
        self.low_sound_button = toga.Button("Select", on_press=self.on_select_low, style=Pack())
        low_row.add(low_sound_label)
        low_row.add(self.low_sound_button)
        if os.path.exists(low_sound_path):
            play_low_button = toga.Button("▶", on_press=lambda w: self.play_sound(low_sound_path), style=Pack(width=40))
            low_row.add(play_low_button)

        # Fila: High
        high_row = toga.Box(style=Pack(direction=ROW, gap=10))
        high_sound_label = toga.Label("High battery sound:", style=Pack(padding=(5, 0)))
        self.high_sound_button = toga.Button("Select", on_press=self.on_select_high, style=Pack())
        high_row.add(high_sound_label)
        high_row.add(self.high_sound_button)
        if os.path.exists(high_sound_path):
            play_high_button = toga.Button("▶", on_press=lambda w: self.play_sound(high_sound_path), style=Pack(width=40))
            high_row.add(play_high_button)

        # Fila: Disconnect
        disconnect_row = toga.Box(style=Pack(direction=ROW, gap=10))
        disconnect_sound_label = toga.Label("Turn off the service sound:", style=Pack(padding=(5, 0)))
        self.disconnect_sound_button = toga.Button("Select", on_press=self.on_select_disconnect, style=Pack())
        disconnect_row.add(disconnect_sound_label)
        disconnect_row.add(self.disconnect_sound_button)
        if os.path.exists(disconnect_sound_path):
            play_disconnect_button = toga.Button("▶", on_press=lambda w: self.play_sound(disconnect_sound_path), style=Pack(width=40))
            disconnect_row.add(play_disconnect_button)

        # Agregar las filas al bloque vertical
        self.sound_column.add(low_row)
        self.sound_column.add(high_row)
        self.sound_column.add(disconnect_row)

        # Agregar los grupos a la fila principal
        self.input_row_2.add(enable_group)

        if default_sound_enabled_json:
            self.input_row_2.add(self.sound_column)

        # Envolver la fila en otro contenedor para centrarla
        centered_row_2_box = toga.Box(
            style=Pack(direction=ROW, justify_content="center")
        )
        centered_row_2_box.add(self.input_row_2)

        # Agregar fila a la ventana principal
        main_box.add(centered_row_2_box)

        # Título 3
        title_3_label = toga.Label(
            "Miscellaneous",
            style=Pack(font_size=20, margin_top=10, margin_bottom=20, text_align="center", alignment="center")
        )
        main_box.add(title_3_label)

        # Fila con para eventos misceláneos obligatorios
        input_row_3 = toga.Box(
            style=Pack(direction=ROW, gap=10, flex=1, alignment="center", justify_content="center")
        )

        closing_notif_label = toga.Label("Enable notifications when closing:", style=Pack(padding=(5, 0)))
        self.closing_notif_checkbox = toga.Switch(
            "",
            style=Pack(),
            value=default_closing_notif_json
        )

        telegram_label = toga.Label("Enable integration with Telegram:", style=Pack(padding=(5, 0)))
        self.telegram_checkbox = toga.Switch(
            "",
            style=Pack(),
            on_change=self.toggle_telegram_fields,
            value=default_msg_telegram_json
        )

        input_row_3.add(closing_notif_label)
        input_row_3.add(self.closing_notif_checkbox)
        input_row_3.add(telegram_label)
        input_row_3.add(self.telegram_checkbox)

        # Envolver la fila en otro contenedor para centrarla
        centered_row_3_box = toga.Box(
            style=Pack(direction=ROW, justify_content="center")
        )
        centered_row_3_box.add(input_row_3)

        # Agregar fila a la ventana principal
        main_box.add(centered_row_3_box)

        # Fila para eventos misceláneos opcionales
        self.input_row_4 = toga.Box(
            style=Pack(direction=ROW, gap=10, flex=1, alignment="center", justify_content="center")
        )

        chat_id_label = toga.Label("Chat ID:", style=Pack(width=90))
        self.chat_id_input = toga.TextInput(
            value=default_chat_id_telegram_json,
            style=Pack(width=100)
        )

        telegram_bot_label = toga.Label("Telegram Bot:", style=Pack(width=90))
        self.telegram_bot_input = toga.TextInput(
            value=default_bot_id_telegram_json,
            style=Pack(width=100)
        )

        self.input_row_4.add(chat_id_label)
        self.input_row_4.add(self.chat_id_input)
        self.input_row_4.add(telegram_bot_label)
        self.input_row_4.add(self.telegram_bot_input)

        # Envolver la fila en otro contenedor para centrarla
        self.centered_row_4_box = toga.Box(
            style=Pack(direction=ROW, justify_content="center")
        )
        
        if default_msg_telegram_json:
            self.centered_row_4_box.add(self.input_row_4)

        # Agregar fila a la ventana principal
        main_box.add(self.centered_row_4_box)

        # Fila para la configuración de sleep y puertos
        self.input_row_5 = toga.Box(
            style=Pack(direction=ROW, gap=10, flex=1, alignment="center", justify_content="center")
        )

        sleep_time_label = toga.Label("Sleep time:", style=Pack(width=90))
        self.sleep_time_input = toga.TextInput(
            value=default_sleep_time_json,
            style=Pack(width=100)
        )

        port_label = toga.Label("Port:", style=Pack(width=90))
        self.port_input = toga.TextInput(
            value=default_port_json,
            style=Pack(width=100)
        )

        self.input_row_5.add(sleep_time_label)
        self.input_row_5.add(self.sleep_time_input)
        self.input_row_5.add(port_label)
        self.input_row_5.add(self.port_input)

        # Envolver la fila en otro contenedor para centrarla
        self.centered_row_5_box = toga.Box(
            style=Pack(direction=ROW, justify_content="center")
        )
        
        if default_msg_telegram_json:
            self.centered_row_5_box.add(self.input_row_5)

        # Agregar fila a la ventana principal
        main_box.add(self.centered_row_5_box)

        # Fila de botones para guardar el contenido
        input_row_6 = toga.Box(
            style=Pack(direction=ROW, gap=10, flex=1, alignment="center", justify_content="center")
        )

        self.accept_button = toga.Button("Aceptar", on_press=self.on_accept, style=Pack(width=100))
        self.cancel_button = toga.Button("Cancelar", on_press=self.on_cancel, style=Pack(width=100))

        input_row_6.add(self.accept_button)
        input_row_6.add(self.cancel_button)

        # Envolver la fila en otro contenedor para centrarla
        centered_row_6_box = toga.Box(
            style=Pack(direction=ROW, justify_content="center", margin_top=10)
        )
        centered_row_6_box.add(input_row_6)

        # Agregar fila a la ventana principal
        main_box.add(centered_row_6_box)


        # Mostrar ventana
        self.main_window = toga.App.BACKGROUND
        self.settings_window = toga.Window(title=self.formal_name, size=(700, 500))
        self.settings_window.content = main_box

        self.settings_window.on_close = self._on_settings_close
        self.windows.add(self.settings_window)
    
    def _on_settings_close(self, window, **kwargs):
        # ocultar en vez de cerrar; devolver False para impedir que Toga destruya la ventana.
        window.hide()
        return False
    
    def show_settings_window(self):
        # método que ejecutaremos desde el thread del tray mediante app.loop.call_soon_threadsafe
        # si la ventana ya está cerrada/recreada, podrías comprobar y volver a crearla
        self.settings_window.show()
        # opcional: intentar dar foco
        try:
            self.settings_window.focus()
        except Exception:
            pass
    
    def show_window(self):
        self.main_window.show()

    def hide_window(self, *args, **kwargs):
        self.main_window.hide()
        return True  # True = evitar que se cierre el app
    
    # Función para validar los inputs de las entradas y que solo se escriban números enteros entre 0 y 100
    def validate_input(self, widget):
        value = widget.value
        if not value.isdigit():
            widget.value = ''.join(filter(str.isdigit, value))
        elif int(value) > 100:
            widget.value = "100"
    
    async def on_select_low(self, widget):
        await self.select_and_copy_sound("battery-low.mp3")

    async def on_select_high(self, widget):
        await self.select_and_copy_sound("battery-high.mp3")
    
    async def on_select_disconnect(self, widget):
        await self.select_and_copy_sound("disconnect.mp3")
    
    async def select_and_copy_sound(self, target_filename):
        # Abrir el explorador de archivos
        file_path = await self.main_window.open_file_dialog(
            title="Selecciona un archivo de sonido",
            file_types=["mp3"]
        )

        if file_path:
            try:
                # Crear el path destino en la carpeta actual / sounds
                current_directory = os.path.dirname(os.path.abspath(__file__))
                sounds_directory = os.path.join(current_directory, 'sounds')
                dest_path = os.path.join(sounds_directory, target_filename)

                if os.path.exists(dest_path):
                    try:
                        os.remove(dest_path)
                    except Exception as e:
                        print("No se pudo eliminar el archivo existente: " + str(e))
                        return

                # Copiar y sobreescribir si ya existe
                shutil.copyfile(file_path, dest_path)
                print("Archivo copiado como: " + str(dest_path))
            except Exception as e:
                print("Error al copiar el archivo: " + str(e))
    
    def toggle_sounds_fields(self, widget):
        if widget.value:
            self.input_row_2.add(self.sound_column)
        else:
            self.input_row_2.remove(self.sound_column)
    
    def toggle_telegram_fields(self, widget):
        if widget.value:
            self.centered_row_4_box.add(self.input_row_4)
        else:
            self.centered_row_4_box.remove(self.input_row_4)
    
    def play_sound(self, filename):
        def _play():
            try:
                playsound(filename)
            except Exception as e:
                print("Error al reproducir sonido: " + str(e))

        # Ejecutar en hilo para no bloquear la interfaz
        threading.Thread(target=_play, daemon=True).start()
    
    async def on_accept(self, widget):
        try:
            self.save_config()
            print("Configuration saved successfully.")
            self.settings_window.hide()
        except Exception as e:
            print("Error saving configuration:", e)
            await self.settings_window.info_dialog("Error", "Error saving configuration: " + str(e))
            self.settings_window.hide()

    def save_config(self):
        config_data = {
            "lower": int(self.min_percentage_input.value) if self.min_percentage_input.value.isdigit() else 0,
            "higher": int(self.max_percentage_input.value) if self.max_percentage_input.value.isdigit() else 100,
            "sound": self.enable_sounds_checkbox.value,
            "closing": self.closing_notif_checkbox.value,
            "msgTelegram": self.telegram_checkbox.value,
            "chatIdTelegram": self.chat_id_input.value,
            "botIdTelegram": self.telegram_bot_input.value,
            "sleepTime": int(self.sleep_time_input.value),
            "port": int(self.port_input.value)
        }

        current_directory = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_directory, "conf.json")

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)

    def on_cancel(self, widget):
        self.settings_window.hide()

def tray_icon(app_instance):
    def on_clicked(icon, item):
        try:
            app_instance.loop.call_soon_threadsafe(app_instance.show_settings_window)
        except Exception as e:
            print("Error al pedir mostrar la ventana:", e)

    icon = pystray.Icon(
        "test",
        create_image(),
        menu=pystray.Menu(
            pystray.MenuItem('Mostrar ventana', on_clicked),
            pystray.MenuItem('Salir', lambda icon, item: sys.exit())
        )
    )
    icon.run()


def socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 5000))
        s.listen()
        print("Servidor escuchando en localhost:5000")
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    print("Mensaje recibido:", data.decode())
                    conn.sendall(b"OK")

if __name__ == "__main__":
    app = NotificationsApp("NotificationsApp", "org.example.notifications")

    # Iniciar servidor en segundo plano
    threading.Thread(target=socket_server, daemon=True).start()

    # Iniciar icono de bandeja en segundo plano
    threading.Thread(target=tray_icon, args=(app,), daemon=True).start()

    # Iniciar la app de Toga
    app.main_loop()