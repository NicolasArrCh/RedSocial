import firebase_admin
from firebase_admin import credentials, db
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static, DataTable
from datetime import datetime  # ✅ Para manejar la fecha y hora


# 🔹 Configurar Firebase
cred = credentials.Certificate("project_credentials.json")  # Reemplaza con tu JSON de credenciales
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://tribucode-85a86-default-rtdb.firebaseio.com/"
})


# 🔹 Referencias
ref = db.reference("posts")


# 🔹 Aplicación con Textual
class PublicacionesApp(App):
    """Aplicación de publicaciones usando Textual."""

    TITLE = "📌 Publicaciones App"

    def compose(self) -> ComposeResult:
        """Define la estructura de la interfaz."""
        yield Header()
        yield Static("📝 Agregar una publicación", classes="title")
        yield Input(placeholder="Nickname", id="nickname")  # Campo para el nickname
        yield Input(placeholder="Título", id="titulo")
        yield Input(placeholder="Contenido", id="contenido")
        yield Button("Publicar", id="btn_publicar", variant="success")
        yield Static("📚 Publicaciones Guardadas", classes="title")
        yield DataTable(id="tabla_publicaciones")
        yield Footer()

    def on_mount(self):
        """Ejecutado cuando la aplicación inicia."""
        # Ya no se mostrarán las publicaciones desde JSON
        pass

    def on_button_pressed(self, event: Button.Pressed):
        """Maneja el evento del botón."""
        if event.button.id == "btn_publicar":
            self.agregar_publicacion()

    def agregar_publicacion(self):
        """Agrega una publicación solo en Firebase."""
        # Obtener el nickname, título y contenido
        nickname = self.query_one("#nickname", Input).value.strip()
        titulo = self.query_one("#titulo", Input).value.strip()
        contenido = self.query_one("#contenido", Input).value.strip()

        if not nickname or not titulo or not contenido:
            self.notify("❌ Error: Nickname, Título y contenido no pueden estar vacíos.", severity="error")
            return

        # ✅ Obtener la fecha y hora actual
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Crear la publicación con 0 likes y 0 comentarios
        nueva_pub = {
            "nickname": nickname,
            "titulo": titulo,
            "contenido": contenido,
            "fecha_hora": fecha_hora,
            "likes": 0,  # Por defecto 0 likes
            "comentarios": 0  # Por defecto 0 comentarios
        }

        # 🔹 Guardar en Firebase
        ref.push(nueva_pub)

        # Limpiar los campos
        self.query_one("#nickname", Input).value = ""
        self.query_one("#titulo", Input).value = ""
        self.query_one("#contenido", Input).value = ""

        self.notify("✅ Publicación guardada con éxito!", severity="success")
        # Ya no se mostrarán las publicaciones
        pass


# 🔹 Ejecutar la aplicación
if __name__ == "__main__":
    PublicacionesApp().run()