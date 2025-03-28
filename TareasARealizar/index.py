import os
import firebase_admin
import bcrypt
from firebase_admin import credentials, db
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Vertical, Center
from textual.widgets import Input, Button, Label, Static
from textual import on

# Obtener la ruta del archivo de credenciales de Firebase
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "project_credentials.json")
DATABASE_URL = "https://tribucode-85a86-default-rtdb.firebaseio.com/"

# Verificar si Firebase ya está inicializado
if not firebase_admin._apps:
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"Archivo de credenciales no encontrado: {CREDENTIALS_PATH}")
    
    cred = credentials.Certificate(CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})

usuarios_ref = db.reference("users")

def hash_password(password):
    """Encripta la contraseña con bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def cargar_registros():
    """Carga los registros de usuarios desde Firebase."""
    registros = usuarios_ref.get()
    return registros if registros else {}

def guardar_registro(nuevo_usuario):
    """Guarda un nuevo usuario en Firebase."""
    usuarios_ref.push(nuevo_usuario)

def calcular_edad(fecha_nacimiento):
    """Calcula la edad a partir de la fecha de nacimiento."""
    try:
        fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        return edad
    except ValueError:
        return None  

class RegistroApp(App):

    CSS = """
    Screen {
        align: center middle;
    }
<<<<<<< HEAD

=======
    
>>>>>>> origin/5-visualización-de-otros-usuarios
    .title {
        text-align: center;
        color: #0FDBA8;
        margin-bottom: 1;
    }

    .form {
<<<<<<< HEAD
        border: round #0FDBA8;
        padding: 2;
        width: 50;
=======
        border: round #0FDBA8;  
        padding: 2;
        width: 40;
>>>>>>> origin/5-visualización-de-otros-usuarios
    }

    Input {
        width: 100%;
        border: solid #0FDBA8;
        margin-bottom: 1;
    }

    Button {
        width: 100%;
        background: #0FDBA8;
        color: black;
        margin-top: 1;
    }

    Button:hover {
        background: #0BCB90;
    }

    .error {
        color: red;
        text-align: center;
    }

    .success {
        color: green;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(classes="form"):
<<<<<<< HEAD
                yield Static("🚀 Registro de Usuario", classes="title")

                self.nombre = Input(placeholder="Nombre")
                self.apellido = Input(placeholder="Apellido")
                self.nickname = Input(placeholder="Nickname")
                self.fecha_nacimiento = Input(placeholder="Fecha de Nacimiento (YYYY-MM-DD)")
                self.correo = Input(placeholder="Correo Electrónico")
                self.genero = Input(placeholder="Género")
                self.pais = Input(placeholder="País")
                self.telefono = Input(placeholder="Teléfono")
                self.contraseña = Input(password=True, placeholder="Contraseña")  
                self.mensaje = Static("", classes="error")

                yield self.nombre
                yield self.apellido
                yield self.nickname
                yield self.fecha_nacimiento
                yield self.correo
                yield self.genero
                yield self.pais
                yield self.telefono
                yield self.contraseña
                yield Button("✅ Registrar", id="registrar")
                yield Button("❌ Cancelar", id="cancelar")
                yield self.mensaje

    @on(Button.Pressed, "#registrar")
    def handle_register(self, event: Button.Pressed) -> None:
        self.registrar_usuario()

    @on(Button.Pressed, "#cancelar")
    def handle_cancel(self, event: Button.Pressed) -> None:
        self.limpiar_campos()

    def registrar_usuario(self):
        """Registra un nuevo usuario en Firebase."""
        registros = cargar_registros()

        nuevo_usuario = {
            "nickname": self.nickname.value.strip(),
            "nombre": self.nombre.value.strip(),
            "apellido": self.apellido.value.strip(),
            "correo": self.correo.value.strip(),
            "fecha_nacimiento": self.fecha_nacimiento.value.strip(),
            "genero": self.genero.value.strip(),
            "pais": self.pais.value.strip(),
            "telefono": self.telefono.value.strip(),
            "contraseña": hash_password(self.contraseña.value.strip())
        }

        # Validar campos vacíos
        if not all(nuevo_usuario.values()):
            self.show_message("⚠️ Todos los campos son obligatorios.", error=True)
            return

        # Validar edad
        edad = calcular_edad(nuevo_usuario["fecha_nacimiento"])
        if edad is None:
            self.show_message("⚠️ Formato de fecha incorrecto. Usa YYYY-MM-DD.", error=True)
            return
        elif edad < 18:
            self.show_message("❌ Debes ser mayor de 18 años para registrarte.", error=True)
            return

        # Verificar si ya existe en Firebase
        for user_id, usuario in registros.items():
            if usuario["nickname"] == nuevo_usuario["nickname"]:
                self.show_message("⚠️ El nickname ya está registrado.", error=True)
                return
            if usuario["correo"] == nuevo_usuario["correo"]:
                self.show_message("⚠️ El correo ya está registrado.", error=True)
                return
            if usuario["telefono"] == nuevo_usuario["telefono"]:
                self.show_message("⚠️ El número de teléfono ya está registrado.", error=True)
                return

        # Guardar usuario en Firebase
        guardar_registro(nuevo_usuario)
        self.show_message("✅ Usuario registrado correctamente.", success=True)
        self.limpiar_campos()

    def limpiar_campos(self):
        """Limpia todos los campos del formulario."""
        self.nombre.value = ""
        self.apellido.value = ""
        self.nickname.value = ""
        self.fecha_nacimiento.value = ""
        self.correo.value = ""
        self.genero.value = ""
        self.pais.value = ""
        self.telefono.value = ""
        self.contraseña.value = ""
        self.show_message("🧹 Formulario limpiado.", success=True)

    def show_message(self, text, success=False, error=False):
        """Muestra mensajes en la interfaz"""
        self.mensaje.update(text)
        self.mensaje.remove_class("success")
        self.mensaje.remove_class("error")
        if success:
            self.mensaje.add_class("success")
        if error:
            self.mensaje.add_class("error")

if __name__ == "__main__":
    RegistroApp().run()
=======
                yield Static("🚀 TribuCode - Iniciar Sesión", classes="title")
                
                yield Label("👤 Usuario:")
                self.user_input = Input(placeholder="Ingresa tu usuario", id="user")
                yield self.user_input

                yield Label("🔒 Contraseña:")  
                self.pass_input = Input(password=True, placeholder="Ingresa tu contraseña", id="password")
                yield self.pass_input  

                self.login_button = Button("✅ Iniciar Sesión", id="login_button")  
                yield self.login_button

                self.message = Static("", classes="error")
                yield self.message

    @on(Button.Pressed, "#login_button")  
    def handle_login(self, event: Button.Pressed) -> None:  
        usuario = self.user_input.value.strip()
        contraseña = self.pass_input.value.strip()

        if not usuario or not contraseña:
            self.show_message("⚠️ Todos los campos son obligatorios.", error=True)
            return

        # Obtener todos los usuarios
        users_ref = db.reference("users").get()
        if not users_ref:
            self.show_message("❌ No hay usuarios registrados.", error=True)
            return

        # Buscar el usuario por nickname
        user_data = None
        for user_id, data in users_ref.items():
            if data.get("nickname") == usuario:
                user_data = data
                break

        if not user_data:
            self.show_message("❌ Usuario no encontrado.", error=True)
            return

        # Verificar la contraseña encriptada
        stored_password = user_data.get("contraseña", "")

        if not stored_password.startswith("$2b$"):
            if contraseña == stored_password:
                self.show_message(f"✅ Bienvenido, {usuario}!", success=True)
            if __name__ == "__main__":
                print("=== INICIANDO APLICACIÓN ===")
                app = RedSocialApp(usuario_registrado=usuario)
                app.run()

            else:
                self.show_message("❌ Usuario o contraseña incorrectos.", error=True)
        elif bcrypt.checkpw(contraseña.encode("utf-8"), stored_password.encode("utf-8")):
            self.show_message(f"✅ Bienvenido, {usuario}!", success=True)
            if __name__ == "__main__":
                print("=== INICIANDO APLICACIÓN ===")
                app = RedSocialApp(usuario_registrado=usuario)
                app.run()
            
        else:
            self.show_message("❌ Usuario o contraseña incorrectos.", error=True)

    def show_message(self, text, success=False, error=False):
        """Muestra mensajes en la interfaz"""
        self.message.update(text)
        self.message.remove_class("success")
        self.message.remove_class("error")
        if success:
            self.message.add_class("success")
        if error:
            self.message.add_class("error")

if __name__ == "__main__":
    TribuCodeLogin().run()
>>>>>>> origin/5-visualización-de-otros-usuarios
