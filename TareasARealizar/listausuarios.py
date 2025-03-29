from textual.app import App
from textual.widgets import DataTable, Input
from firebase_admin import credentials, db
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
    """Widget to display and filter users."""
    
    def compose(self):
        """Create child widgets."""
        yield Input(placeholder="Filtrar por nombre, apellido, genero o pais", id="filtro")
        yield DataTable(id="tabla")

    def on_mount(self):
        """Set up the widget when it's mounted."""
        self.tabla = self.query_one("#tabla", DataTable)
        self.filtro = self.query_one("#filtro", Input)
        self.tabla.add_columns("Nombre", "Apellido", "Usuario", "Genero", "Pais", "Correo")
        self.obtener_datos()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """React to input changes."""
        if event.input.id == "filtro":
            self.filtrar_datos(event.value)
    
    def obtener_datos(self):
        """Get data from Firebase."""
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
        self.actualizar_tabla(self.datos_completos)
    
    def filtrar_datos(self, texto_filtro):
        """Filter data based on input text."""
        filtro = texto_filtro.lower().strip()
        
        if not filtro:
            self.actualizar_tabla(self.datos_completos)
            return
    
        datos_filtrados = []
        for fila in self.datos_completos:
            if (filtro in str(fila[0]).lower() or  
                filtro in str(fila[1]).lower() or  
                filtro in str(fila[2]).lower() or 
                filtro in str(fila[3]).lower() or  
                filtro in str(fila[4]).lower()):   
                datos_filtrados.append(fila)
    
        self.actualizar_tabla(datos_filtrados)
    
    def actualizar_tabla(self, datos):
        """Update the table with the provided data."""
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
    """Main application class."""
    
    def compose(self):
        """Create child widgets."""
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
