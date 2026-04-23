from fastapi import HTTPException
from app.repositories import apps_repo
from datetime import date 

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
                                                                                                                                                          
def reportar_uso(hijo_id: str, minutos: int):                                                                                                                                                   
    try:
        hoy = str(date.today())
        uso = apps_repo.get_uso_hoy(hijo_id, hoy)
        if uso:
            apps_repo.actualizar_uso(uso[0]["id"], minutos)
        else:
            apps_repo.crear_uso({"hijo_id": hijo_id, "fecha": hoy, "minutos_usados": minutos})
        return {"mensaje": "Uso reportado", "minutos_usados": minutos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def obtener_estado(hijo_id: str):
    try:
        from app.repositories import usuarios_repo
        hoy = str(date.today())
        uso = apps_repo.get_uso_hoy(hijo_id, hoy)
        minutos_usados = uso[0]["minutos_usados"] if uso else 0

        hijo = usuarios_repo.get_by_id(hijo_id)
        if not hijo:
            raise HTTPException(status_code=404, detail="Hijo no encontrado")
        limite = hijo[0].get("tiempo_limite_minutos") or 120

        bloqueado = minutos_usados >= limite
        return {
            "hijo_id": hijo_id,
            "minutos_usados": minutos_usados,
            "tiempo_limite_minutos": limite,
            "bloqueado": bloqueado,
            "minutos_restantes": max(0, limite - minutos_usados)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))