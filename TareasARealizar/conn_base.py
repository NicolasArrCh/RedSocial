import firebase_admin
from firebase_admin import credentials, db

class FirebaseDB:
    def __init__(self, credential_path, database_url):
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
