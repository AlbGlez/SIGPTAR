from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import UserMixin

class Usuario(UserMixin):
    
    def __init__(self, id, nombre_usuario, clave, rol_id=-1, nombre="", apellido_paterno="", apellido_materno="", telefono_movil=-1, activo=-1):
        self.id=id
        self.nombre_usuario=nombre_usuario
        self.clave=clave
        self.rol_id=rol_id
        self.nombre=nombre
        self.apellido_paterno=apellido_paterno
        self.apellido_materno=apellido_materno
        self.telefono_movil=telefono_movil
        self.activo=activo
        
    @classmethod
    def verifica_clave(self, hashed_clave, clave):
        return check_password_hash(hashed_clave, clave)
    
#print(generate_password_hash('albglez'))
        