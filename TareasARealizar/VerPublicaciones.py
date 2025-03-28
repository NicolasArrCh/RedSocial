import firebase_admin
import traceback
from firebase_admin import credentials, db
from conn_base import FirebaseDB
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static
from textual.containers import ScrollableContainer
import threading
from datetime import datetime

path = "./project_credentials.json"
url = "https://tribucode-85a86-default-rtdb.firebaseio.com/"

fb_db = FirebaseDB(path, url)

# Inicialización de Firebase
firebase_db = FirebaseDB(CREDENTIAL_PATH, DATABASE_URL)

def obtener_publicaciones():
    """Obtiene publicaciones específicamente del nodo /posts"""
    try:
        print("\n🔍 Buscando publicaciones en /posts...")
        posts = firebase_db.read_record("/posts")
        
        if not posts:
            print("⚠️ No se encontraron publicaciones en /posts")
            return []
        
        print(f"📊 Total de publicaciones encontradas: {len(posts)}")
        
        lista_publicaciones = []
        for post_id, post_data in posts.items():
            if not isinstance(post_data, dict):
                print(f"✖ Ignorando {post_id} - no es un diccionario")
                continue
                
            print(f"\n🔹 Procesando publicación ID: {post_id}")
            print("📄 Datos crudos:", post_data)
            
            publicacion = {
                "id": post_id,
                "usuario": post_data.get("nickname", "Anónimo"),
                "titulo": post_data.get("titulo", "Sin título"),
                "contenido": post_data.get("contenido", ""),
                "likes": int(post_data.get("likes", 0)),
                "comentarios": int(post_data.get("comentarios", 0)),
                "fecha_hora": post_data.get("fecha_hora", "")
            }
            
            if publicacion["fecha_hora"]:
                try:
                    fecha_obj = datetime.strptime(publicacion["fecha_hora"], "%Y-%m-%d %H:%M:%S")
                    publicacion["fecha_formateada"] = fecha_obj.strftime("%d/%m/%Y %H:%M")
                except Exception as e:
                    print(f"⚠️ Error al formatear fecha: {e}")
                    publicacion["fecha_formateada"] = publicacion["fecha_hora"]
            else:
                publicacion["fecha_formateada"] = "Fecha desconocida"
            
            lista_publicaciones.append(publicacion)
        
        lista_publicaciones.sort(
            key=lambda x: datetime.strptime(x["fecha_hora"], "%Y-%m-%d %H:%M:%S") if x["fecha_hora"] else datetime.min,
            reverse=True
        )
        
        return lista_publicaciones
        
    except Exception as e:
        print(f"❌ Error crítico al obtener publicaciones: {str(e)}")
        traceback.print_exc()
        return []

class PublicacionWidget(Static):
    def __init__(self, publicacion, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publicacion = publicacion
        self.styles.border = ("round", "#6272a4")
        self.styles.padding = (1, 2)
        self.styles.margin = (0, 0, 1, 0)
        self.styles.background = "#282a36"

    def compose(self) -> ComposeResult:
        yield Static(
            f"📌 [b]{self.publicacion['titulo']}[/b]\n"
            f"👤 [b]{self.publicacion['usuario']}[/b] • "
            f"📅 {self.publicacion['fecha_formateada']}",
            classes="publicacion-header"
        )
        yield Static(
            f"\n{self.publicacion['contenido']}\n",
            classes="publicacion-contenido"
        )
        yield Static(
            f"❤️ [b]{self.publicacion['likes']}[/b] likes • "
            f"💬 [b]{self.publicacion['comentarios']}[/b] comentarios",
            classes="publicacion-footer"
        )

class RedSocialApp(App):
    CSS = """
    Screen {
        background: #1e1e2e;
        color: #f8f8f2;
    }
    #header-container {
        layout: horizontal;
        width: 100%;
        margin-bottom: 1;
    }
    #search-container {
        width: 60%;
    }
    #user-info {
        width: 40%;
        text-align: right;
        color: #89b4fa;
        padding-right: 2;
    }
    #contenedor-publicaciones {
        width: 100%;
        height: 78vh;
        overflow-y: auto;
        padding: 1;
    }
    .publicacion-header {
        color: #89b4fa;
        margin-bottom: 1;
    }
    .publicacion-contenido {
        color: #cdd6f4;
        margin: 1 0;
        padding: 1;
        background: #313244;
        border: round #585b70;
    }
    .publicacion-footer {
        color: #a6adc8;
        margin-top: 1;
    }
    #filtro-busqueda {
        width: 100%;
        border: round #585b70;
    }
    #mensaje-estado {
        margin: 1 0;
        color: #a6e3a1;
    }
    """
    
    def __init__(self, usuario_registrado="Usuario", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario_registrado = usuario_registrado
    
    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="header-container"):
            with ScrollableContainer(id="search-container"):
                yield Input(placeholder="🔍 Buscar...", id="filtro-busqueda")
            yield Static(f"👤 {self.usuario_registrado}", id="user-info")
        self.mensaje_estado = Static("Cargando publicaciones...", id="mensaje-estado")
        yield self.mensaje_estado
        yield ScrollableContainer(id="contenedor-publicaciones")
        yield Footer()
    
    def on_mount(self) -> None:
        self.cargar_publicaciones()
    
    def cargar_publicaciones(self, filtro: str = ""):
        def _cargar(filtro_texto: str):
            try:
                publicaciones = obtener_publicaciones()
                if filtro_texto:
                    filtro_lower = filtro_texto.lower()
                    publicaciones = [
                        p for p in publicaciones
                        if (filtro_lower in p["usuario"].lower() or
                            filtro_lower in p["titulo"].lower() or
                            filtro_lower in p["contenido"].lower())
                    ]
                self.call_from_thread(self.mostrar_publicaciones, publicaciones)
            except Exception as e:
                print(f"Error al cargar publicaciones: {e}")
                self.call_from_thread(
                    self.query_one("#mensaje-estado").update,
                    f"Error: {str(e)}"
                )
        
        threading.Thread(target=_cargar, args=(filtro,), daemon=True).start()
    
    def mostrar_publicaciones(self, publicaciones: list):
        contenedor = self.query_one("#contenedor-publicaciones")
        contenedor.remove_children()
        
        if not publicaciones:
            self.mensaje_estado.update("No se encontraron publicaciones")
            return
        
        for pub in publicaciones:
            contenedor.mount(PublicacionWidget(pub))
        
        self.mensaje_estado.update(f"Mostrando {len(publicaciones)} publicaciones")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        self.cargar_publicaciones(event.value.strip())

if __name__ == "__main__":
    print("=== INICIANDO APLICACIÓN ===")
    app = RedSocialApp(usuario_registrado="Brayan")
    app.run()