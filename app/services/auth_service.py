from fastapi import HTTPException
from app.repositories import auth_repo


def registro(data):
    try:
        auth_response = auth_repo.sign_up(data.email, data.password)
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Error al crear usuario")

        perfil = {"id": auth_response.user.id, "email": data.email, "nombre": data.nombre, "rol": data.rol}
        auth_repo.create_perfil(perfil)

        return {
            "mensaje": "Usuario registrado exitosamente",
            "user_id": auth_response.user.id,
            "email": data.email,
            "nombre": data.nombre,
            "rol": data.rol
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def login(data):
    try:
        auth_response = auth_repo.sign_in(data.email, data.password)
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        perfil = auth_repo.get_perfil(auth_response.user.id)
        return {
            "mensaje": "Login exitoso",
            "access_token": auth_response.session.access_token,
            "user_id": auth_response.user.id,
            "perfil": perfil[0] if perfil else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def logout():
    try:
        auth_repo.sign_out()
        return {"mensaje": "Sesion cerrada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def vincular_hijo(hijo_id: str, padre_id: str):
    try:
        data = auth_repo.vincular_hijo(hijo_id, padre_id)
        if not data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"mensaje": "Hijo vinculado al padre exitosamente", "data": data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def registro_hijo(data, padre_id: str):
    try:
        auth_response = auth_repo.sign_up(data.email, data.password)
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Error al crear cuenta del hijo")

        perfil = {
            "id": auth_response.user.id,
            "email": data.email,
            "nombre": data.nombre,
            "rol": "hijo",
            "padre_id": padre_id,
            "edad": data.edad
        }
        auth_repo.create_perfil(perfil)

        return {
            "mensaje": "Hijo registrado exitosamente",
            "user_id": auth_response.user.id,
            "nombre": data.nombre,
            "padre_id": padre_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def recuperar_password(email: str):
    try:
        auth_repo.reset_password(email)
        return{"mensaje": "Correo de recuperación enviado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=set(e))

def cambiar_password(access_token: str, nueva_password: str):
    try:
        auth_repo.cambiar_password(access_token, nueva_password)
        return {"mensaje": "Contraseña actualizada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))