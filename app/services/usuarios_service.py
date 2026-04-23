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
