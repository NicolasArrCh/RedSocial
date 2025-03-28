import firebase_admin
from firebase_admin import credentials, db
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, Static, ListView, ListItem
from textual.containers import Vertical, Horizontal
import os
import json
from datetime import datetime
from class_firebase_database import *

# Configuración de Firebase
path = "./project_credentials.json"

url ="https://tribucode-85a86-default-rtdb.firebaseio.com/"

fb_db=FirebaseDB(path, url)
def inicializar_firebase():
    """Inicializa la conexión con Firebase si no está ya inicializada."""
    if not os.path.exists(path):
        print("[!] Aquí deberían ir las credenciales reales de Firebase.")
        print("[!] Crea un archivo credenciales.json con tu configuración.")
        exit(1)

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(path)
            app = firebase_admin.initialize_app(cred, {'databaseURL': url})
            print(f"[DEBUG] Firebase inicializado con éxito para {app.name}")
    except Exception as e:
        print(f"[!] Error al inicializar Firebase: {e}")
        exit(1)

# Módulo para la interfaz de gestión y publicación
class GestionPublicacion(App):
    """Interfaz de Textual similar a Twitter para listar usuarios y crear publicaciones."""
    
    TITLE = "Mini Twitter"
    
    CSS = """
    Static { width: 100%; padding: 1; }
    ListView { height: auto; max-height: 20; border: solid white; }
    Input { margin: 1; width: 50%; }
    Button { margin: 1; }
    #publicaciones { margin-top: 1; }
    #usuario_actual { color: cyan; }
    .reacciones { padding: 1; border: solid gray; }
    """

    def __init__(self, usuario, nombre):
        super().__init__()
        self.usuario = usuario
        self.nombre = nombre
        inicializar_firebase()

    def compose(self) -> ComposeResult:
        """Composición de la interfaz similar a Twitter."""
        yield Header()
        yield Vertical(
            Static(f"@{self.usuario} ({self.nombre})", id="usuario_actual"),
            Horizontal(
                Input(placeholder="¿Qué está pasando?", id="mensaje_input"),
                Button("Tweet", id="btn_publicar", variant="primary")
            ),
            Button("Ver Lista de Usuarios", id="btn_lista_usuarios"),
            ListView(id="publicaciones"),
            ListView(id="lista_usuarios", classes="hidden"),
            Button("Volver al Menú", id="btn_volver", variant="warning")
        )
        yield Footer()

    def on_mount(self) -> None:
        """Cargar publicaciones al iniciar."""
        self.cargar_publicaciones()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejo de eventos de botones."""
        if event.button.id == "btn_publicar":
            self.crear_publicacion()
        elif event.button.id == "btn_lista_usuarios":
            self.listar_usuarios()
        elif event.button.id == "btn_volver":
            self.exit()
        elif event.button.id.startswith("react_"):
            self.agregar_reaccion(event.button.id)

    def crear_publicacion(self):
        """Crear una publicación en Firebase con formato Twitter."""
        mensaje_input = self.query_one("#mensaje_input", Input)
        mensaje = mensaje_input.value.strip()
        if mensaje:
            try:
                ref = db.reference('publicaciones')
                nueva_pub = ref.push()
                hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                nueva_pub.set({
                    'nombre': self.nombre,
                    'usuario': self.usuario,
                    'hora': hora,
                    'mensaje': mensaje,
                    'reacciones': {
                        'me_gusta': 0,
                        'me_encanta': 0,
                        'me_sorprende': 0,
                        'me_enoja': 0
                    },
                    'comentarios': []
                })
                self.notify("Tweet publicado con éxito!", severity="information")
                mensaje_input.value = ""
                self.cargar_publicaciones()
            except Exception as e:
                self.notify(f"Error al crear publicación: {e}", severity="error")
        else:
            self.notify("El tweet no puede estar vacío.", severity="error")

    def listar_usuarios(self):
        """Listar usuarios registrados desde Firebase."""
        lista = self.query_one("#lista_usuarios", ListView)
        publicaciones = self.query_one("#publicaciones", ListView)
        lista.clear()
        try:
            ref = db.reference('usuarios')
            usuarios = ref.get()
            if usuarios:
                for usuario, datos in usuarios.items():
                    nombre = datos.get('nombre', 'Desconocido')
                    lista.append(ListItem(Static(f"@{usuario} ({nombre})")))
                lista.remove_class("hidden")
                publicaciones.add_class("hidden")
                self.notify("Lista de usuarios actualizada.", severity="information")
            else:
                self.notify("No hay usuarios registrados.", severity="warning")
        except Exception as e:
            self.notify(f"Error al listar usuarios: {e}", severity="error")

    def cargar_publicaciones(self):
        """Cargar y mostrar publicaciones desde Firebase con reacciones."""
        publicaciones = self.query_one("#publicaciones", ListView)
        lista_usuarios = self.query_one("#lista_usuarios", ListView)
        publicaciones.clear()
        try:
            ref = db.reference('publicaciones')
            posts = ref.get()
            if posts:
                for post_id, datos in posts.items():
                    nombre = datos.get('nombre', 'Desconocido')
                    usuario = datos.get('usuario', 'Anon')
                    hora = datos.get('hora', 'Sin fecha')
                    mensaje = datos.get('mensaje', 'Sin mensaje')
                    reacciones = datos.get('reacciones', {})
                    tweet = f"{nombre} @{usuario} · {hora}\n{mensaje}"
                    
                    # Contenedor para publicación y reacciones
                    contenedor = Vertical(
                        Static(tweet),
                        Horizontal(
                            Button(f"Me gusta ({reacciones.get('me_gusta', 0)})", id=f"react_me_gusta_{post_id}"),
                            Button(f"Me encanta ({reacciones.get('me_encanta', 0)})", id=f"react_me_encanta_{post_id}"),
                            Button(f"Me sorprende ({reacciones.get('me_sorprende', 0)})", id=f"react_me_sorprende_{post_id}"),
                            Button(f"Me enoja ({reacciones.get('me_enoja', 0)})", id=f"react_me_enoja_{post_id}"),
                            classes="reacciones"
                        )
                    )
                    publicaciones.append(ListItem(contenedor))
                publicaciones.remove_class("hidden")
                lista_usuarios.add_class("hidden")
            else:
                publicaciones.append(ListItem(Static("No hay tweets aún.")))
                publicaciones.remove_class("hidden")
                lista_usuarios.add_class("hidden")
        except Exception as e:
            self.notify(f"Error al cargar publicaciones: {e}", severity="error")

    def agregar_reaccion(self, button_id: str):
        """Agregar una reacción a una publicación."""
        partes = button_id.split('_')
        tipo_reaccion = '_'.join(partes[1:-1])  # me_gusta, me_encanta, etc.
        post_id = partes[-1]
        
        try:
            ref = db.reference(f'publicaciones/{post_id}/reacciones/{tipo_reaccion}')
            valor_actual = ref.get() or 0
            ref.set(valor_actual + 1)
            self.notify(f"Reacción '{tipo_reaccion.replace('_', ' ')}' añadida!", severity="information")
            self.cargar_publicaciones()  # Actualizar la interfaz
        except Exception as e:
            self.notify(f"Error al añadir reacción: {e}", severity="error")

# Función para ejecutar el módulo
def ejecutar_gestion_publicacion(usuario, nombre):
    """Iniciar la interfaz de gestión y publicación."""
    app = GestionPublicacion(usuario, nombre)
    app.run()

if __name__ == "__main__":
    # Prueba local
    usuario_prueba = "evelin"
    nombre_prueba = "Evelin Pérez"
    print(f"Simulando sesión con @{usuario_prueba} ({nombre_prueba})")
    ejecutar_gestion_publicacion(usuario_prueba, nombre_prueba)