import bcrypt
from class_firebase_database import FirebaseDB
from firebase_admin import db
from textual.app import App, ComposeResult
from textual.containers import Vertical, Center
from textual.widgets import Input, Button, Label, Static
from textual.message import Message
from textual import on
from utilizarCrud import *

# Configuración de Firebase
path = "./project_credentials.json"
url = "https://tribucode-85a86-default-rtdb.firebaseio.com/"

fb_db = FirebaseDB(path, url)

class TribuCodeLogin(App):

    CSS = """
    Screen {
        align: center middle;
    }
    
    .title {
        text-align: center;
        color: #0FDBA8;
        margin-bottom: 1;
    }

    .form {
        border: round #0FDBA8;  
        padding: 2;
        width: 40;
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

            else:
                self.show_message("❌ Usuario o contraseña incorrectos.", error=True)
        elif bcrypt.checkpw(contraseña.encode("utf-8"), stored_password.encode("utf-8")):
            self.show_message(f"✅ Bienvenido, {usuario}!", success=True)
            
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