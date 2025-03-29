import firebase_admin
from firebase_admin import credentials, db
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, Static, ListView, ListItem
from textual.containers import Vertical, Horizontal
import os
from datetime import datetime

# Configuración centralizada de Firebase
def inicializar_firebase():
    """Inicializa Firebase solo si no está inicializado"""
    if not firebase_admin._apps:
        try:
            path = os.path.join(os.path.dirname(__file__), "project_credentials.json")
            if not os.path.exists(path):
                raise FileNotFoundError("Credenciales de Firebase no encontradas")
            
            cred = credentials.Certificate(path)
            url = "https://tribucode-85a86-default-rtdb.firebaseio.com/"
            firebase_admin.initialize_app(cred, {"databaseURL": url})
            print("[✓] Firebase inicializado correctamente")
        except Exception as e:
            print(f"[!] Error crítico con Firebase: {e}")
            exit(1)

inicializar_firebase()

class GestionPublicacion(App):
    """Interfaz de Textual para gestión de publicaciones estilo Twitter"""
    
    TITLE = "Mini Twitter"
    CSS = """
    Screen {
        background: #1e1e2e;
        color: #f8f8f2;
    }
    Static { 
        width: 100%; 
        padding: 1; 
    }
    ListView { 
        height: auto; 
        max-height: 20; 
        border: solid #6272a4; 
        margin: 1 0;
    }
    Input { 
        margin: 1; 
        width: 50%; 
    }
    Button { 
        margin: 1; 
    }
    #usuario_actual { 
        color: #89b4fa; 
        text-style: bold;
    }
    .reacciones { 
        padding: 1; 
        border: solid #585b70; 
        margin-top: 1;
    }
    .hidden {
        display: none;
    }
    """

    def __init__(self, usuario, nombre):
        super().__init__()
        self.usuario = usuario
        self.nombre = nombre
        self.datos_publicaciones = []

    def compose(self) -> ComposeResult:
        """Composición de la interfaz"""
        yield Header()
        yield Vertical(
            Static(f"@{self.usuario} ({self.nombre})", id="usuario_actual"),
            Horizontal(
                Input(placeholder="¿Qué está pasando?", id="mensaje_input"),
                Button("Publicar", id="btn_publicar", variant="primary")
            ),
            Button("Ver Usuarios", id="btn_lista_usuarios"),
            ListView(id="lista_publicaciones"),
            ListView(id="lista_usuarios", classes="hidden"),
            Button("Volver", id="btn_volver", variant="warning")
        )
        yield Footer()

    def on_mount(self) -> None:
        """Cargar publicaciones al iniciar"""
        self.cargar_publicaciones()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejo de eventos de botones"""
        if event.button.id == "btn_publicar":
            self.crear_publicacion()
        elif event.button.id == "btn_lista_usuarios":
            self.mostrar_usuarios()
        elif event.button.id == "btn_volver":
            self.mostrar_publicaciones()
        elif event.button.id.startswith("react_"):
            self.agregar_reaccion(event.button.id)

    def crear_publicacion(self):
        """Crear una nueva publicación en Firebase"""
        mensaje_input = self.query_one("#mensaje_input", Input)
        mensaje = mensaje_input.value.strip()
        
        if not mensaje:
            self.notify("El mensaje no puede estar vacío", severity="error")
            return

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
            
            self.notify("Publicación creada con éxito", severity="success")
            mensaje_input.value = ""
            self.cargar_publicaciones()
            
        except Exception as e:
            self.notify(f"Error al publicar: {str(e)}", severity="error")

    def cargar_publicaciones(self):
        """Cargar publicaciones desde Firebase"""
        try:
            ref = db.reference('publicaciones')
            publicaciones = ref.get() or {}
            self.datos_publicaciones = []
            
            for post_id, datos in publicaciones.items():
                self.datos_publicaciones.append({
                    'id': post_id,
                    'nombre': datos.get('nombre', 'Anónimo'),
                    'usuario': datos.get('usuario', 'anon'),
                    'hora': datos.get('hora', 'Sin fecha'),
                    'mensaje': datos.get('mensaje', ''),
                    'reacciones': datos.get('reacciones', {})
                })
            
            self.mostrar_publicaciones()
            
        except Exception as e:
            self.notify(f"Error al cargar publicaciones: {str(e)}", severity="error")

    def mostrar_publicaciones(self):
        """Mostrar publicaciones en la interfaz"""
        lista_pub = self.query_one("#lista_publicaciones", ListView)
        lista_usu = self.query_one("#lista_usuarios", ListView)
        
        lista_pub.clear()
        lista_pub.remove_class("hidden")
        lista_usu.add_class("hidden")
        
        if not self.datos_publicaciones:
            lista_pub.append(ListItem(Static("No hay publicaciones aún")))
            return
        
        for pub in sorted(self.datos_publicaciones, 
                         key=lambda x: x['hora'], reverse=True):
            tweet = f"{pub['nombre']} @{pub['usuario']} · {pub['hora']}\n{pub['mensaje']}"
            
            contenedor = Vertical(
                Static(tweet),
                Horizontal(
                    Button(f"👍 {pub['reacciones'].get('me_gusta', 0)}", 
                          id=f"react_me_gusta_{pub['id']}"),
                    Button(f"❤️ {pub['reacciones'].get('me_encanta', 0)}", 
                          id=f"react_me_encanta_{pub['id']}"),
                    Button(f"😮 {pub['reacciones'].get('me_sorprende', 0)}", 
                          id=f"react_me_sorprende_{pub['id']}"),
                    Button(f"😠 {pub['reacciones'].get('me_enoja', 0)}", 
                          id=f"react_me_enoja_{pub['id']}"),
                    classes="reacciones"
                )
            )
            lista_pub.append(ListItem(contenedor))

    def mostrar_usuarios(self):
        """Mostrar lista de usuarios"""
        try:
            ref = db.reference('usuarios')
            usuarios = ref.get() or {}
            
            lista_usu = self.query_one("#lista_usuarios", ListView)
            lista_pub = self.query_one("#lista_publicaciones", ListView)
            
            lista_usu.clear()
            lista_usu.remove_class("hidden")
            lista_pub.add_class("hidden")
            
            for usuario_id, datos in usuarios.items():
                nombre = datos.get('nombre', 'Desconocido')
                lista_usu.append(ListItem(Static(f"@{usuario_id} ({nombre})")))
                    
        except Exception as e:
            self.notify(f"Error al cargar usuarios: {str(e)}", severity="error")

    def agregar_reaccion(self, button_id: str):
        """Añadir reacción a una publicación"""
        try:
            _, tipo, post_id = button_id.split('_', 2)
            ref = db.reference(f'publicaciones/{post_id}/reacciones/{tipo}')
            ref.set((ref.get() or 0) + 1)
            self.cargar_publicaciones()
        except Exception as e:
            self.notify(f"Error al añadir reacción: {str(e)}", severity="error")

def ejecutar_gestion_publicacion(usuario: str, nombre: str):
    """Iniciar la aplicación de publicaciones"""
    app = GestionPublicacion(usuario, nombre)
    app.run()

if __name__ == "__main__":
    # Datos de prueba
    ejecutar_gestion_publicacion(
        usuario="usuario_prueba",
        nombre="Usuario de Prueba"
    )