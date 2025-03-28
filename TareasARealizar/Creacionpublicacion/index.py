from class_firebase_database import FirebaseDB
from firebase_admin import db
import json

path = r"./project_credentials.json"

url ="https://tribucode-85a86-default-rtdb.firebaseio.com/"

fb_db=FirebaseDB(path, url)

ref=db.reference('users')
new_id_user=ref.push()
new_id_user.set({
        "nickname":"Juanito123",
        "nombre": "Juan",
        "apellido": "Pérez",
        "correo": "juan@example.com",
        "fecha_nacimiento": "1990-05-12",
        "genero": "Masculino",
        "pais": "Colombia",
        "telefono": "+573001234567",
        "contraseña":"12345678"
    })
# fb_db.write_record('users/Juanito123', data_user)
ref=db.reference('posts')
new_id_post=ref.push()
new_id_post.set({
    "post_id": "P001",
    "nickname": "Juanito123",
    "contenido": "¡Hola, mundo!",
    "fecha": "2025-03-26",
    "likes":"0",
    "comentarios":"0"
})


