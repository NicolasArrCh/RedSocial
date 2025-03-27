import firebase_admin
from firebase_admin import credentials, db
from conn_base import FirebaseDB
import json
from datetime import datetime

# Configuración de Firebase
CREDENTIAL_PATH = "/home/sebastian/Escritorio/CampusLands/MiRedSocial/RedSocial/TareasARealizar/publicacionesapp-439d1-firebase-adminsdk-fbsvc-8ce7a03e01.json"
DATABASE_URL = "https://publicacionesapp-439d1-default-rtdb.firebaseio.com/"

def inicializar_firebase():
    """Inicializa Firebase solo si no está inicializado"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(CREDENTIAL_PATH)
        firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
        print("✅ Firebase inicializado correctamente")
    return db.reference()

def subir_publicacion_prueba():
    """Sube una publicación de prueba a Firebase"""
    try:
        ref = inicializar_firebase()
        
        # Datos de la publicación de prueba
        publicacion_prueba = {
            "usuario": "UsuarioPrueba",
            "contenido": "Esta es una publicación de prueba generada automáticamente",
            "likes": 0,
            "comentarios": {
                "com1": {
                    "usuario": "OtroUsuario",
                    "texto": "Primer comentario de prueba"
                }
            },
            "fecha": datetime.now().isoformat(),
            "ID": "pub_prueba_" + datetime.now().strftime("%Y%m%d%H%M%S")
        }
        
        # Subir la publicación
        ref.child("publicaciones").child(publicacion_prueba["ID"]).set(publicacion_prueba)
        print(f"📤 Publicación de prueba subida con ID: {publicacion_prueba['ID']}")
        
        return publicacion_prueba["ID"]
    except Exception as e:
        print(f"❌ Error al subir publicación: {str(e)}")
        return None

def verificar_publicacion(id_publicacion):
    """Verifica que una publicación existe y muestra sus datos"""
    try:
        ref = inicializar_firebase()
        publicacion = ref.child("publicaciones").child(id_publicacion).get()
        
        if publicacion:
            print("\n🔍 Publicación encontrada:")
            print(json.dumps(publicacion, indent=2, ensure_ascii=False))
            return True
        else:
            print("⚠️ La publicación no existe")
            return False
    except Exception as e:
        print(f"❌ Error al verificar publicación: {str(e)}")
        return False

def listar_todas_publicaciones():
    """Lista todas las publicaciones en la base de datos"""
    try:
        ref = inicializar_firebase()
        publicaciones = ref.child("publicaciones").get()
        
        print("\n📜 Listado completo de publicaciones:")
        if publicaciones:
            for pub_id, pub_data in publicaciones.items():
                print(f"\n🆔 ID: {pub_id}")
                print(f"👤 Usuario: {pub_data.get('usuario', 'Desconocido')}")
                print(f"📝 Contenido: {pub_data.get('contenido', 'Sin contenido')}")
                print(f"❤️ Likes: {pub_data.get('likes', 0)}")
                print(f"💬 Comentarios: {len(pub_data.get('comentarios', {}))}")
                print(f"📅 Fecha: {pub_data.get('fecha', 'No especificada')}")
        else:
            print("No hay publicaciones en la base de datos")
    except Exception as e:
        print(f"❌ Error al listar publicaciones: {str(e)}")

if __name__ == "__main__":
    print("=== PRUEBA DE PUBLICACIONES ===")
    
    # 1. Subir publicación de prueba
    print("\n1. Subiendo publicación de prueba...")
    id_prueba = subir_publicacion_prueba()
    
    if id_prueba:
        # 2. Verificar la publicación
        print("\n2. Verificando publicación...")
        if verificar_publicacion(id_prueba):
            print("✅ Publicación verificada correctamente")
        else:
            print("❌ No se pudo verificar la publicación")
        
        # 3. Listar todas las publicaciones
        print("\n3. Listando todas las publicaciones...")
        listar_todas_publicaciones()
    
    print("\n=== PRUEBA COMPLETADA ===")