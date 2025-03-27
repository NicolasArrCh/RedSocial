import firebase_admin
from firebase_admin import credentials, db
from conn_base import FirebaseDB
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static
from textual.containers import ScrollableContainer
import threading
from datetime import datetime

# Configuración de Firebase
CREDENTIAL_PATH = "/home/sebastian/Escritorio/CampusLands/MiRedSocial/RedSocial/TareasARealizar/tribucode-85a86-firebase-adminsdk-fbsvc-d1ff3ccd74.json"
DATABASE_URL = "https://tribucode-85a86-default-rtdb.firebaseio.com/"

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
            # Verificar que sea una publicación válida
            if not isinstance(post_data, dict):
                print(f"✖ Ignorando {post_id} - no es un diccionario")
                continue
                
            print(f"\n🔹 Procesando publicación ID: {post_id}")
            print("📄 Datos crudos:", post_data)
            
            # Extraer datos con valores por defecto
            publicacion = {
                "id": post_id,
                "usuario": post_data.get("nickname", "Anónimo"),
                "titulo": post_data.get("titulo", "Sin título"),
                "contenido": post_data.get("contenido", ""),
                "likes": int(post_data.get("likes", 0)),
                "comentarios_count": int(post_data.get("comentarios", 0)),
                "fecha_hora": post_data.get("fecha_hora", "")
            }
            
            # Formatear fecha
            if publicacion["fecha_hora"]:
                try:
                    fecha_obj = datetime.strptime(publicacion["fecha_hora"], "%Y-%m-%d %H:%M:%S")
                    publicacion["fecha_formateada"] = fecha_obj.strftime("%d/%m/%Y %H:%M")
                except Exception as e:
                    print(f"⚠️ Error al formatear fecha: {e}")
                    publicacion["fecha_formateada"] = publicacion["fecha_hora"]
            else:
                publicacion["fecha_formateada"] = "Fecha desconocida"
            
            print("🔄 Datos procesados:", publicacion)
            lista_publicaciones.append(publicacion)
        
        # Ordenar por fecha (más reciente primero)
        lista_publicaciones.sort(
            key=lambda x: datetime.strptime(x["fecha_hora"], "%Y-%m-%d %H:%M:%S") if x["fecha_hora"] else datetime.min,
            reverse=True
        )
        
        return lista_publicaciones
        
    except Exception as e:
        print(f"❌ Error crítico al obtener publicaciones: {str(e)}")
        return []

class PublicacionWidget(Static):
    """Widget para mostrar cada publicación"""
    def __init__(self, publicacion, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publicacion = publicacion
        self.styles.border = ("round", "#6272a4")
        self.styles.padding = (1, 2)
        self.styles.margin = (0, 0, 1, 0)
        self.styles.background = "#282a36"

    def compose(self) -> ComposeResult:
        # Cabecera con título y usuario
        yield Static(
            f"📌 [b]{self.publicacion['titulo']}[/b]\n"
            f"👤 [b]{self.publicacion['usuario']}[/b] • "
            f"📅 {self.publicacion['fecha_formateada']}",
            classes="publicacion-header"
        )
        
        # Contenido
        yield Static(
            f"\n{self.publicacion['contenido']}\n",
            classes="publicacion-contenido"
        )
        
        # Pie con likes y comentarios
        yield Static(
            f"❤️ [b]{self.publicacion['likes']}[/b] likes • "
            f"💬 [b]{self.publicacion['comentarios_count']}[/b] comentarios",
            classes="publicacion-footer"
        )

class RedSocialApp(App):
    CSS = """
    Screen {
        background: #1e1e2e;
        color: #f8f8f2;
    }
    
    #contenedor-publicaciones {
        width: 100%;
        height: 80vh;
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
        margin-bottom: 1;
        border: round #585b70;
    }
    
    #mensaje-estado {
        margin: 1 0;
        color: #a6e3a1;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="🔍 Buscar por usuario, título o contenido...", id="filtro-busqueda")
        self.mensaje_estado = Static("Cargando publicaciones...", id="mensaje-estado")
        yield self.mensaje_estado
        yield ScrollableContainer(id="contenedor-publicaciones")
        yield Footer()
    
    def on_mount(self) -> None:
        """Al iniciar la aplicación"""
        self.cargar_publicaciones()
    
    def cargar_publicaciones(self, filtro: str = ""):
        """Carga las publicaciones con filtrado opcional"""
        def _cargar():
            publicaciones = obtener_publicaciones()
            
            if filtro:
                filtro_lower = filtro.lower()
                publicaciones = [
                    p for p in publicaciones
                    if (filtro_lower in p["usuario"].lower() or
                        filtro_lower in p["titulo"].lower() or
                        filtro_lower in p["contenido"].lower())
                ]
            
            self.call_from_thread(self.mostrar_publicaciones, publicaciones)
        
        threading.Thread(target=_cargar, daemon=True).start()
    
    def mostrar_publicaciones(self, publicaciones: list):
        """Muestra las publicaciones en la interfaz"""
        contenedor = self.query_one("#contenedor-publicaciones")
        contenedor.remove_children()
        
        if not publicaciones:
            self.mensaje_estado.update("No se encontraron publicaciones")
            return
        
        for publicacion in publicaciones:
            contenedor.mount(PublicacionWidget(publicacion))
        
        self.mensaje_estado.update(f"Mostrando {len(publicaciones)} publicaciones")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filtra las publicaciones cuando cambia el texto de búsqueda"""
        self.cargar_publicaciones(event.value.strip())

if __name__ == "__main__":
    print("=== INICIANDO APLICACIÓN ===")
    app = RedSocialApp()
    app.run()