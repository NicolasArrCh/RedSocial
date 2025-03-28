from textual.app import *
from textual.widgets import *
from firebase_admin import credentials, db
from textual.widgets import DataTable, TabbedContent, TabPane, Label, Input, Button
import firebase_admin
from textual.containers import Vertical

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://tribucode-85a86-default-rtdb.firebaseio.com/"
})
class UsuariosWidget(Vertical):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filtrar", id="filtro")
        yield Button("Buscar", id="btn_buscar")
        yield DataTable(id="tabla")

    def on_mount(self) -> None:
        self.tabla = self.query_one("#tabla", DataTable)
        self.filtro = self.query_one("#filtro", Input)
        self.btn_buscar = self.query_one("#btn_buscar", Button)
        self.tabla.add_columns("Nombre", "Apellido", "Usuario", "Genero", "Pais", "Correo")
        self.btn_buscar.on_click = self.filtrar_datos
        self.obtener_datos()

    def obtener_datos(self):
        ref = db.reference("/users")
        datos = ref.get() or {}
        self.datos = [
            [str(row.get("nombre", "")), row.get("apellido", ""), row.get("nickname", ""), row.get("genero", ""), row.get("pais", ""), str(row.get("correo", ""))]
            for row in datos.values()
        ]
        self.actualizar_tabla(self.datos)

    def actualizar_tabla(self, datos):
        self.tabla.clear()
        for fila in datos:
            self.tabla.add_row(*fila)
            
    def filtrar_datos(self):
        filtro = self.filtro.value.lower().strip()
        if filtro:
            datos_filtrados = [fila for fila in self.datos if filtro in fila[1].lower() or filtro in fila[2].lower() or filtro in fila[3].lower()]
        else:
            datos_filtrados = self.datos
        self.actualizar_tabla(datos_filtrados)
            
class JsonListApp(App):
    def compose(self) -> ComposeResult:
        yield UsuariosWidget()
        
JsonListApp().run()