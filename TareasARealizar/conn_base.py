import firebase_admin
from firebase_admin import credentials, db
import os

class FirebaseDB:
    def __init__(self, credential_path, database_url):
        # Verifica que el archivo existe antes de intentar usarlo
        if not os.path.exists(credential_path):
            raise FileNotFoundError(f"El archivo de credenciales '{credential_path}' no se encuentra en la ruta esperada.")

        # Evitar inicializar Firebase más de una vez
        if not firebase_admin._apps:
            cred = credentials.Certificate(credential_path)
            firebase_admin.initialize_app(cred, {"databaseURL": database_url})

    def write_record(self, path, data):
        ref = db.reference(path)
        ref.set(data)

    def read_record(self, path):
        ref = db.reference(path)
        return ref.get()

    def update_record(self, path, data):
        ref = db.reference(path)
        ref.update(data)

    def delete_record(self, path):
        ref = db.reference(path)
        ref.delete()

