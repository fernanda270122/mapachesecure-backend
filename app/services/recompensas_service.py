from fastapi import HTTPException
from app.repositories import recompensas_repo, desafios_repo, catalogo_repo

def obtener_recompensas(hijo_id: str):
    try:
        return recompensas_repo.get_by_hijo(hijo_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def crear_recompensa(recompensa):
    try:
        result = recompensas_repo.create(recompensa.model_dump())
        return {"mensaje": "Recompensa creada exitosamente 🎁", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def canjear_recompensa(data):
    try:
        recompensa = recompensas_repo.get_by_id(data.recompensa_id)
        if not recompensa:
            raise HTTPException(status_code=404, detail="Recompensa no encontrada")

        costo = recompensa[0]["costo_puntos"]

        puntos_data = desafios_repo.get_puntos(data.hijo_id)
        puntos_actuales = puntos_data[0]["total_puntos"] if puntos_data else 0

        if puntos_actuales < costo:
            return {
                "mensaje": "No tienes suficientes puntos 😢",
                "puntos_actuales": puntos_actuales,
                "puntos_necesarios": costo
            }

        recompensas_repo.registrar_canje({"hijo_id": data.hijo_id, "recompensa_id": data.recompensa_id})
        return {
            "mensaje": "¡Recompensa canjeada exitosamente! 🦝🎉",
            "puntos_gastados": costo,
            "puntos_restantes": puntos_actuales - costo
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def historial_canjes(hijo_id: str):
    try:
        return recompensas_repo.get_historial_canjes(hijo_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
                                                                                                                                                
def obtener_catalogo():
    try:
        return catalogo_repo.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def agregar_al_catalogo(datos, padre_id: str):
    try:
        nuevo = datos.model_dump()
        nuevo["creado_por"] = padre_id
        result = catalogo_repo.create(nuevo)
        return {"mensaje": "Recompensa agregada al catálogo 🎁", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def eliminar_del_catalogo(catalogo_id: str, padre_id: str):
    try:
        result = catalogo_repo.delete(catalogo_id, padre_id)
        if not result:
            raise HTTPException(status_code=403, detail="No puedes eliminar esta recompensa")
        return {"mensaje": "Recompensa eliminada del catálogo"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))