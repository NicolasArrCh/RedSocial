import bcrypt
import asyncio
import os
from firebase_admin import db, credentials
from textual.app import App, ComposeResult
from textual.containers import Vertical, Center
from textual.widgets import Input, Button, Label, Static
from textual import on
from VerPublicaciones import RedSocialApp
from registrar import RegistroApp  # Importamos la clase de registro

# Configuración de Firebase
path = os.path.join(os.path.dirname(__file__), "project_credentials.json")
cred = credentials.Certificate(path)
url = "https://tribucode-85a86-default-rtdb.firebaseio.com/"

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
                self.registro_button = Button("📌 Regístrate", id="registro_button")
                yield self.registro_button  # Botón de registro
                self.message = Static("", classes="error")
                yield self.message

    @on(Button.Pressed, "#login_button")
    def handle_login(self, event: Button.Pressed) -> None:
        usuario = self.user_input.value.strip()
        contraseña = self.pass_input.value.strip()

        if not usuario or not contraseña:
            self.show_message("⚠️ Todos los campos son obligatorios.", error=True)
            return

        # Obtener todos los usuarios desde Firebase
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
        if (stored_password.startswith("$2b$") and bcrypt.checkpw(contraseña.encode("utf-8"), stored_password.encode("utf-8"))) or contraseña == stored_password:
            self.show_message(f"✅ Bienvenido, {usuario}!", success=True)

            # Ocultar el formulario de inicio de sesión correctamente
            form = self.query_one(".form")
            form.remove()

            # Mostrar la aplicación principal
            app = RedSocialApp(usuario_registrado=usuario)
            asyncio.create_task(app.run_async())  # Ejecutar de forma asíncrona
        else:
            self.show_message("❌ Usuario o contraseña incorrectos.", error=True)

    @on(Button.Pressed, "#registro_button")
    def handle_register(self, event: Button.Pressed) -> None:
        """Oculta el formulario de inicio de sesión y abre la pantalla de registro"""
        form = self.query_one(".form")
        form.remove()  # Oculta el formulario de inicio de sesión antes de abrir el registro

        # Iniciar la ventana de registro
        registro_app = RegistroApp()
        asyncio.create_task(registro_app.run_async())

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
