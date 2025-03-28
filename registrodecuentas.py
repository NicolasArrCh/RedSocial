from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Button, Label, Static
import json
from datetime import datetime

ARCHIVO_JSON = "registrocuentas.json"

def cargar_registros():
    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_registros(registros):
    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)

def calcular_edad(fecha_nacimiento):
    try:
        fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        return edad
    except ValueError:
        return None  

class RegistroApp(App):
    def compose(self) -> ComposeResult:
        yield Label("Registro de Usuario")
        self.nombre = Input(placeholder="Nombre")
        self.apellido = Input(placeholder="Apellido")
        self.nickname = Input(placeholder="Nickname")
        self.fecha_nacimiento = Input(placeholder="Fecha de Nacimiento (YYYY-MM-DD)")
        self.correo = Input(placeholder="Correo Electrónico")
        self.genero = Input(placeholder="Género")
        self.pais = Input(placeholder="País")
        self.telefono = Input(placeholder="Teléfono")
        self.contraseña = Input(placeholder="Contraseña", password=True)  # Campo de contraseña
        self.mensaje = Static("", classes="mensaje")
        
        yield Vertical(
            self.nombre, self.apellido, self.nickname,
            self.fecha_nacimiento, self.correo, self.genero,
            self.pais, self.telefono, self.contraseña,
            Button("Registrar", id="registrar"),
            Button("Cancelar", id="cancelar"),
            self.mensaje
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "registrar":
            self.registrar_usuario()
        elif event.button.id == "cancelar":
            self.limpiar_campos()

    def registrar_usuario(self):
        registros = cargar_registros()
        
        nuevo_usuario = {
            "Nombre": self.nombre.value.strip(),
            "Apellido": self.apellido.value.strip(),
            "Nickname": self.nickname.value.strip(),
            "Fecha de Nacimiento": self.fecha_nacimiento.value.strip(),
            "Correo Electrónico": self.correo.value.strip(),
            "Género": self.genero.value.strip(),
            "País": self.pais.value.strip(),
            "Teléfono": self.telefono.value.strip(),
            "Contraseña": self.contraseña.value.strip()
        }
        
       
        if not all(nuevo_usuario.values()):
            self.mensaje.update("Todos los campos son obligatorios.")
            return
        
    
        edad = calcular_edad(nuevo_usuario["Fecha de Nacimiento"])
        if edad is None:
            self.mensaje.update("Formato de fecha incorrecto. Usa YYYY-MM-DD.")
            return
        elif edad < 18:
            self.mensaje.update("Debes ser mayor de 18 años para registrarte.")
            return

       
        for usuario in registros:
            if usuario["Nickname"] == nuevo_usuario["Nickname"]:
                self.mensaje.update("El nickname ya está registrado.")
                return
            if usuario["Correo Electrónico"] == nuevo_usuario["Correo Electrónico"]:
                self.mensaje.update("El correo ya está registrado.")
                return
            if usuario["Teléfono"] == nuevo_usuario["Teléfono"]:
                self.mensaje.update("El número de teléfono ya está registrado.")
                return

        # Guardar usuario en el JSON
        registros.append(nuevo_usuario)
        guardar_registros(registros)
        self.mensaje.update("Usuario registrado correctamente.")
        self.limpiar_campos()

    def limpiar_campos(self):
        self.nombre.value = ""
        self.apellido.value = ""
        self.nickname.value = ""
        self.fecha_nacimiento.value = ""
        self.correo.value = ""
        self.genero.value = ""
        self.pais.value = ""
        self.telefono.value = ""
        self.contraseña.value = ""
        self.mensaje.update("Formulario limpiado.")

if __name__ == "__main__":
    RegistroApp().run()
