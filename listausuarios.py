import json
from textual.app import *
from textual.widgets import *


class JsonListApp(App):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        with open("registrocuentas.json", "r") as file:
            data = json.load(file)
        
        table = self.query_one(DataTable)
        table.add_columns(*data[0].keys())
        for row in data:
            table.add_row(*map(str, row.values()))

JsonListApp().run()




