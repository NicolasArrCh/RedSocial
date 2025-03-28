from textual.app import App
from textual.widgets import DataTable, Input
from firebase_admin import credentials, db
from textual.containers import Vertical
import firebase_admin

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://tribucode-85a86-default-rtdb.firebaseio.com/"
})

class UsuariosWidget(Vertical):
    """Widget to display and filter users."""
    
    def compose(self):
        """Create child widgets."""
        yield Input(placeholder="Filtrar por nombre, apellido, genero o pais", id="filtro")
        yield DataTable(id="tabla")

    def on_mount(self):
        """Set up the widget when it's mounted."""
        self.tabla = self.query_one("#tabla", DataTable)
        self.tabla.add_columns("Nombre", "Apellido", "Usuario", "Genero", "Pais", "Correo")
        self.obtener_datos()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """React to input changes."""
        if event.input.id == "filtro":
            self.filtrar_datos(event.value)
    
    def obtener_datos(self):
        """Get data from Firebase."""
        ref = db.reference("/users")
        datos = ref.get() or {}
        self.datos_completos = [
            [row.get("nombre", ""), row.get("apellido", ""), row.get("nickname", ""),
              row.get("genero", ""), row.get("pais", ""), row.get("correo", "")]
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

class JsonListApp(App):
    """Main application class."""
    
    def compose(self):
        """Create child widgets."""
        yield UsuariosWidget()



JsonListApp().run()