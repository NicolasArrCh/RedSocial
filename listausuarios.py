import json
from textual.app import *
from textual.widgets import *
from firebase_admin import credentials, db
from textual.widgets import DataTable, TabbedContent, TabPane

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://publicacionesapp-439d1.firebaseio.com"
})
class JsonListApp(App):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Usuarios"):
                yield DataTable()

    def on_mount(self) -> None:
        ref = db.reference("/registrocuentas")
        data = ref.get() or {}
        
        table = self.query_one(DataTable)
        columnas = ["Nombre", "Apellido", "Usuario", "Genero", "Pais", "Correo"]
        table.add_columns(*columnas)
        for row in data:
            table.add_row(str(row["nombre"]), row["apellido"], str(row["usuario"]), row["genero"], str(row["pais"]), row["correo"])

JsonListApp().run()




