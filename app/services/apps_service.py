from fastapi import HTTPException
from app.repositories import apps_repo


def obtener_apps_bloqueadas(hijo_id: str):
    try:
        return apps_repo.get_by_hijo(hijo_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def agregar_app_bloqueada(app):
    try:
        result = apps_repo.create(app.model_dump())
        return {"mensaje": "App bloqueada agregada exitosamente", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def eliminar_app_bloqueada(app_id: str):
    try:
        apps_repo.delete(app_id)
        return {"mensaje": "App desbloqueada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def verificar_app(hijo_id: str, package_name: str):
    try:
        data = apps_repo.get_by_hijo_y_package(hijo_id, package_name)
        if data:
            return {"bloqueada": True, "requiere_desafio": data[0]["requiere_desafio"], "data": data[0]}
        return {"bloqueada": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
