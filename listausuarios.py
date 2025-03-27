from textual.app import *
from textual.widgets import *
from firebase_admin import credentials, db
from textual.widgets import DataTable, TabbedContent, TabPane
import firebase_admin
from textual.containers import Vertical

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://tribucode-85a86-default-rtdb.firebaseio.com/"
})
class JsonListApp(App):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Usuarios"):
                with Vertical():
                    yield Label("Lista de Usuarios")
                    yield DataTable(id="tabla")

    def on_mount(self) -> None:
        self.tabla = self.query_one("#tabla", DataTable)
        self.tabla.add_columns("Nombre", "Apellido", "Usuario", "Genero", "Pais", "Correo")
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
JsonListApp().run()




