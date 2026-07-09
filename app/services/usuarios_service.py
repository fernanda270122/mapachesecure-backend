from fastapi import HTTPException
from app.repositories import usuarios_repo


def obtener_usuarios():
    try:
        return usuarios_repo.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def obtener_usuario(usuario_id: str):
    try:
        data = usuarios_repo.get_by_id(usuario_id)
        if not data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def crear_usuario(usuario):
    try:
        datos = {k: v for k, v in usuario.model_dump().items() if v is not None}
        return usuarios_repo.create(datos)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def obtener_hijos(padre_id: str):
    try:
        return usuarios_repo.get_hijos(padre_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def configurar_hijo(hijo_id: str, config):
    try:
        datos = {"tiempo_limite_minutos": config.tiempo_limite_minutos}
        result = usuarios_repo.update(hijo_id, datos)
        return {"mensaje": "Configuración actualizada", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def actualizar_tipo_avatar(usuario_id: str, tipo_avatar: str):
    try:
        avatares_validos = {'mago', 'dormilon', 'gamer', 'ninja', 'samuray', 'princes'}
        if tipo_avatar not in avatares_validos:
            raise HTTPException(status_code=400, detail="Avatar no válido")
        usuarios_repo.update(usuario_id, {"tipo_avatar": tipo_avatar})
        return {"mensaje": "Avatar actualizado", "tipo_avatar": tipo_avatar}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def actualizar_foto_perfil(usuario_id: str, foto_perfil: str):
    try:
        usuarios_repo.update(usuario_id, {"foto_perfil": foto_perfil})
        return {"mensaje": "Foto de perfil actualizada", "foto_perfil": foto_perfil}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def eliminar_usuario(usuario_id: str):
    try:
        usuarios_repo.delete(usuario_id)
        return {"mensaje": "Usuario eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
