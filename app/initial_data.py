# /app/initial_data.py

import asyncio
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.db import models, schemas
from app.services import user_service

# --- IMPORTANTE ---
# Asegúrate de que las tablas estén creadas antes de intentar insertar datos.
# Esta línea es redundante si main.py ya la ejecutó, pero es segura de correr de nuevo.
Base.metadata.create_all(bind=engine)

# Obtener una sesión de base de datos
db: Session = SessionLocal()

async def create_initial_user():
    print("Verificando si el usuario administrador ya existe...")
    
    # Comprobar si ya existe un usuario con ese nombre o email
    user = user_service.get_user_by_username(db, username="admin")
    
    if user:
        print("El usuario 'admin' ya existe. No se tomará ninguna acción.")
    else:
        print("Creando usuario 'admin'...")
        
        # Datos del nuevo superusuario
        user_in = schemas.UserCreate(
            username="admin",
            email="admin@gmail.com",  # Puedes cambiar este email
            password="David*2017",
            is_active=True
        )
        
        # Usamos el servicio para crear el usuario (que se encarga del hashing)
        new_user = user_service.create_user(db, user_in=user_in)
        
        # Hacemos que sea administrador
        new_user.is_admin = True
        db.add(new_user)
        db.commit()
        
        print("¡Superusuario 'admin' creado con éxito!")
        print("Contraseña: admin")

    # Cerrar la sesión de la base de datos
    db.close()

if __name__ == "__main__":
    # Ejecutar la función asíncrona
    # En versiones modernas de Python, puedes simplemente llamar a await en el nivel superior,
    # pero para compatibilidad, usamos asyncio.run()
    asyncio.run(create_initial_user())