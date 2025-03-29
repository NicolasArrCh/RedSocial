from textual.app import *
from textual.widgets import *
from firebase_admin import credentials, db
from textual.widgets import DataTable, TabbedContent, TabPane, Label, Input, Button
import firebase_admin
from textual.containers import Vertical
import os
import traceback

# Configuración de Firebase
if not firebase_admin._apps:
    path = os.path.join(os.path.dirname(__file__), "project_credentials.json")
    cred = credentials.Certificate(path)
    url = "https://tribucode-85a86-default-rtdb.firebaseio.com/"
    firebase_admin.initialize_app(cred, {"databaseURL": url})

class UsuariosWidget(Vertical):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filtrar", id="filtro")
        yield Button("Buscar", id="btn_buscar")
        yield DataTable(id="tabla")

    def on_mount(self) -> None:
        self.tabla = self.query_one("#tabla", DataTable)
        self.filtro = self.query_one("#filtro", Input)
        self.tabla.add_columns("Nombre", "Apellido", "Usuario", "Genero", "Pais", "Correo")
        self.obtener_datos()

    def obtener_datos(self):
        ref = db.reference("/users")
        datos = ref.get()
        if datos is None:
            print("No se encontraron datos en Firebase")
            return
        
        self.datos = [
            [str(row.get("nombre", "")), row.get("apellido", ""), row.get("nickname", ""),
             row.get("genero", ""), row.get("pais", ""), str(row.get("correo", ""))]
            for row in datos.values()
        ]
        self.actualizar_tabla(self.datos)

    def actualizar_tabla(self, datos):
        self.tabla.clear()
        for fila in datos:
            self.tabla.add_row(*fila)
    
    @on(Button.Pressed, "#btn_buscar")
    def filtrar_datos(self, event: Button.Pressed) -> None:
        filtro = self.filtro.value.lower().strip()
        if filtro:
            datos_filtrados = [fila for fila in self.datos if filtro in fila[0].lower() or filtro in fila[1].lower()]
        else:
            datos_filtrados = self.datos
        self.actualizar_tabla(datos_filtrados)

class JsonListApp(App):
    def compose(self) -> ComposeResult:
        yield UsuariosWidget()

if __name__ == "__main__":
    try:
        print("=== INICIANDO APLICACIÓN ===")
        app = JsonListApp()
        app.run()
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        traceback.print_exc()
        exit(1)