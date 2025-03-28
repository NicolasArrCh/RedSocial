import bcrypt
from class_firebase_database import FirebaseDB
from firebase_admin import db
import json

path = r"E:\CAMPUSLAND\Software\4.Scrum\RedSocial\TareasARealizar\InicioDeSesiónDeUsuario\project_credentials.json"
url = "https://tribucode-85a86-default-rtdb.firebaseio.com/"

fb_db = FirebaseDB(path, url)

# Función para hashear la contraseña
def hash_password(password):
    salt = bcrypt.gensalt()  # Genera un salt aleatorio
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hashea la contraseña
    return hashed.decode('utf-8')  # Convierte a string para guardar en Firebase

# Datos del usuario
data_user = {
    "nickname": "camilitashhh",
    "nombre": "Camila Ivanna",
    "apellido": "Dangond Tarazona",
    "correo": "dangonddd@gmail.com",
    "fecha_nacimiento": "2001-06-02",
    "genero": "Femenino",
    "pais": "España",
    "telefono": "3154474789",
    "contraseña": hash_password("Camila2001.")  # Encripta la contraseña
}

# Guardar usuario en Firebase
ref = db.reference('users')
new_id_user = ref.push()
new_id_user.set(data_user)

#"Usuario registrado con contraseña encriptada.

# fb_db.write_record('users/Juanito123', data_user)
ref=db.reference('posts')
new_id_post=ref.push()
new_id_post.set({
    "nickname": "camilitashhh",
    "contenido": "Programar es mi pasión",
    "fecha": "2025-03-27"
})

