import json
from textual.app import *
from textual.widgets import *


class JsonListApp(App):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        with open("usuarios.json", "r") as file:
            data = json.load(file)
        
        table = self.query_one(DataTable)
        columnas = ["Nombre", "Apellido", "Usuario", "Genero", "Pais", "Correo"]
        table.add_columns(*columnas)
        for row in data:
            table.add_row(str(row["nombre"]), row["apellido"], str(row["usuario"]), row["genero"], str(row["pais"]), row["correo"])

JsonListApp().run()




