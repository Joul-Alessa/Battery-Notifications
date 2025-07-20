import json
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class NotificationsApp(toga.App):
    def startup(self):
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
        except Exception as e:
            print("Error leyendo conf.json:", e)
            default_min_json = "0"
            default_max_json = "100"
            default_sound_enabled_json = False
            default_closing_notif_json = True
            default_msg_telegram_json = False
            default_chat_id_telegram_json = ""
            default_bot_id_telegram_json = ""
        
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
        input_row_2 = toga.Box(
            style=Pack(direction=ROW, gap=10, flex=1, alignment="center", justify_content="center")
        )

        enable_sounds_label = toga.Label("Enable sounds notifications:", style=Pack(padding=(5, 0)))
        self.enable_sounds_checkbox = toga.Switch(
            "",
            style=Pack(),
            value=default_sound_enabled_json
        )

        low_sound_label = toga.Label("Low battery sound:", style=Pack(padding=(5, 0)))
        self.low_sound_button = toga.Button("Select", on_press=self.on_select_low, style=Pack())

        high_sound_label = toga.Label("High battery sound:", style=Pack(padding=(5, 0)))
        self.high_sound_button = toga.Button("Select", on_press=self.on_select_high, style=Pack())

        input_row_2.add(enable_sounds_label)
        input_row_2.add(self.enable_sounds_checkbox)
        input_row_2.add(low_sound_label)
        input_row_2.add(self.low_sound_button)
        input_row_2.add(high_sound_label)
        input_row_2.add(self.high_sound_button)

        # Envolver la fila en otro contenedor para centrarla
        centered_row_2_box = toga.Box(
            style=Pack(direction=ROW, justify_content="center")
        )
        centered_row_2_box.add(input_row_2)

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

        # Fila con para eventos misceláneos opcionales
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

        # Fila de botones para guardar el contenido
        input_row_5 = toga.Box(
            style=Pack(direction=ROW, gap=10, flex=1, alignment="center", justify_content="center")
        )

        self.accept_button = toga.Button("Aceptar", on_press=self.on_accept, style=Pack(width=100))
        self.cancel_button = toga.Button("Cancelar", on_press=self.on_cancel, style=Pack(width=100))

        input_row_5.add(self.accept_button)
        input_row_5.add(self.cancel_button)

        # Envolver la fila en otro contenedor para centrarla
        centered_row_5_box = toga.Box(
            style=Pack(direction=ROW, justify_content="center", margin_top=10)
        )
        centered_row_5_box.add(input_row_5)

        # Agregar fila a la ventana principal
        main_box.add(centered_row_5_box)


        # Mostrar ventana
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    
    # Función para validar los inputs de las entradas y que solo se escriban números enteros entre 0 y 100
    def validate_input(self, widget):
        value = widget.value
        if not value.isdigit():
            widget.value = ''.join(filter(str.isdigit, value))
        elif int(value) > 100:
            widget.value = "100"
    
    def on_select_low(self, widget):
        print("Low sound selected")

    def on_select_high(self, widget):
        print("High sound selected")
    
    def toggle_telegram_fields(self, widget):
        if widget.value:
            self.centered_row_4_box.add(self.input_row_4)
        else:
            self.centered_row_4_box.remove(self.input_row_4)
    
    def on_accept(self, widget):
        print("on_accept")
    
    def on_cancel(self, widget):
        print("on_cancel")


def main():
    return NotificationsApp("NotificationsApp", "org.example.notifications")

if __name__ == "__main__":
    main().main_loop()
