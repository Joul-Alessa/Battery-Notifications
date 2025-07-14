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
        except Exception as e:
            print("Error leyendo conf.json:", e)
            default_min_json = "0"
            default_max_json = "100"
            default_sound_enabled_json = False
        
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
        
        main_box.add(centered_row_2_box)

        # Título 3
        title_3_label = toga.Label(
            "Miscellaneous",
            style=Pack(font_size=20, margin_top=10, margin_bottom=20, text_align="center", alignment="center")
        )
        main_box.add(title_3_label)

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


def main():
    return NotificationsApp("NotificationsApp", "org.example.notifications")

if __name__ == "__main__":
    main().main_loop()
