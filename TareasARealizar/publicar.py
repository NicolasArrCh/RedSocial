import firebase_admin
from firebase_admin import credentials, db
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static, DataTable
from datetime import datetime
import os  # Importación faltante
import traceback  # Para manejo de errores

# 🔹 Configurar Firebase
try:
    path = os.path.join(os.path.dirname(__file__), "project_credentials.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo de credenciales: {path}")
        
    cred = credentials.Certificate(path)
    url = "https://tribucode-85a86-default-rtdb.firebaseio.com/"
    
    # Inicializar Firebase solo si no está ya inicializado
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {'databaseURL': url})
    
    ref = db.reference("posts")
except Exception as e:
    print(f"❌ Error al inicializar Firebase: {str(e)}")
    traceback.print_exc()
    exit(1)

# 🔹 Aplicación con Textual
class PublicacionesApp(App):
    """Aplicación de publicaciones usando Textual."""

    TITLE = "📌 Publicaciones App"
    CSS = """
    Screen {
        background: #1e1e2e;
        color: #f8f8f2;
    }
    .title {
        color: #89b4fa;
        margin-bottom: 1;
    }
    #tabla_publicaciones {
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Define la estructura de la interfaz."""
        yield Header()
        yield Static("📝 Agregar una publicación", classes="title")
        yield Input(placeholder="Nickname", id="nickname")
        yield Input(placeholder="Título", id="titulo")
        yield Input(placeholder="Contenido", id="contenido")
        yield Button("Publicar", id="btn_publicar", variant="success")
        yield Static("📚 Publicaciones Guardadas", classes="title")
        yield DataTable(id="tabla_publicaciones")
        yield Footer()

    def on_mount(self):
        """Configura la tabla al iniciar."""
        tabla = self.query_one("#tabla_publicaciones", DataTable)
        tabla.add_columns("Nickname", "Título", "Fecha")
        tabla.cursor_type = "row"

    def on_button_pressed(self, event: Button.Pressed):
        """Maneja el evento del botón."""
        if event.button.id == "btn_publicar":
            self.agregar_publicacion()

    def agregar_publicacion(self):
        """Agrega una publicación a Firebase y actualiza la tabla."""
        try:
            nickname = self.query_one("#nickname", Input).value.strip()
            titulo = self.query_one("#titulo", Input).value.strip()
            contenido = self.query_one("#contenido", Input).value.strip()

            if not all([nickname, titulo, contenido]):
                self.notify("❌ Todos los campos son requeridos", severity="error")
                return

            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            nueva_pub = {
                "nickname": nickname,
                "titulo": titulo,
                "contenido": contenido,
                "fecha_hora": fecha_hora,
                "likes": 0,
                "comentarios": 0
            }

            # Guardar en Firebase
            ref.push(nueva_pub)

            # Actualizar tabla
            tabla = self.query_one("#tabla_publicaciones", DataTable)
            tabla.add_row(nickname, titulo, fecha_hora.split()[0])

            # Limpiar campos
            for field in ["nickname", "titulo", "contenido"]:
                self.query_one(f"#{field}", Input).value = ""

            self.notify("✅ Publicación guardada con éxito!", severity="success")

        except Exception as e:
            self.notify(f"❌ Error al publicar: {str(e)}", severity="error")
            traceback.print_exc()

if __name__ == "__main__":
    try:
        print("=== INICIANDO APLICACIÓN ===")
        app = PublicacionesApp()
        app.run()
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        traceback.print_exc()
        exit(1)