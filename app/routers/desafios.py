from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import supabase
from typing import Optional

router = APIRouter(prefix="/desafios", tags=["Desafios"])

# Modelos
class DesafioCompletar(BaseModel):
    hijo_id: str
    desafio_id: str
    foto_url: Optional[str] = None

# Obtener todos los desafíos
@router.get("/")
def obtener_desafios():
    try:
        response = supabase.table("desafios").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener desafíos por tipo
@router.get("/tipo/{tipo}")
def obtener_por_tipo(tipo: str):
    try:
        response = supabase.table("desafios").select("*").eq("tipo", tipo).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Completar un desafío
@router.post("/completar")
def completar_desafio(data: DesafioCompletar):
    try:
        # Buscar el desafío para obtener los puntos
        desafio = supabase.table("desafios").select("*").eq("id", data.desafio_id).execute()
        if not desafio.data:
            raise HTTPException(status_code=404, detail="Desafío no encontrado")
        
        puntos = desafio.data[0]["puntos"]
        requiere_foto = desafio.data[0]["requiere_foto"]

        # Si requiere foto y no se envió
        if requiere_foto and not data.foto_url:
            return {
                "mensaje": "Este desafío requiere foto como evidencia",
                "validado": False,
                "puntos_otorgados": 0
            }

        # Registrar desafío completado
        registro = {
            "hijo_id": data.hijo_id,
            "desafio_id": data.desafio_id,
            "foto_url": data.foto_url,
            "validado": not requiere_foto,  # Auto-valida si no requiere foto
            "puntos_otorgados": puntos if not requiere_foto else 0
        }

        response = supabase.table("desafios_completados").insert(registro).execute()
        return {
            "mensaje": "¡Desafío completado! 🦝",
            "validado": not requiere_foto,
            "puntos_otorgados": puntos if not requiere_foto else 0,
            "data": response.data[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener desafíos completados por hijo
@router.get("/completados/{hijo_id}")
def obtener_completados(hijo_id: str):
    try:
        response = supabase.table("desafios_completados").select("*").eq("hijo_id", hijo_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener puntos totales de un hijo
@router.get("/puntos/{hijo_id}")
def obtener_puntos(hijo_id: str):
    try:
        response = supabase.table("puntos_por_hijo").select("*").eq("hijo_id", hijo_id).execute()
        if not response.data:
            return {"hijo_id": hijo_id, "total_puntos": 0}
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Validar desafío con foto (el padre aprueba o rechaza)
@router.put("/validar/{desafio_completado_id}")
def validar_desafio(desafio_completado_id: str, aprobado: bool):
    try:
        # Obtener el desafío completado
        registro = supabase.table("desafios_completados").select("*").eq("id", desafio_completado_id).execute()
        if not registro.data:
            raise HTTPException(status_code=404, detail="Desafio no encontrado")

        dato = registro.data[0]

        if aprobado:
            # Obtener puntos del desafío original
            desafio = supabase.table("desafios").select("puntos").eq("id", dato["desafio_id"]).execute()
            puntos = desafio.data[0]["puntos"]

            # Actualizar como validado y otorgar puntos
            supabase.table("desafios_completados").update({
                "validado": True,
                "puntos_otorgados": puntos
            }).eq("id", desafio_completado_id).execute()

            return {
                "mensaje": "Desafio aprobado! Puntos otorgados",
                "puntos_otorgados": puntos
            }
        else:
            # Rechazar sin otorgar puntos
            supabase.table("desafios_completados").update({
                "validado": False,
                "puntos_otorgados": 0
            }).eq("id", desafio_completado_id).execute()

            return {
                "mensaje": "Desafio rechazado",
                "puntos_otorgados": 0
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener desafíos pendientes de validación por padre
@router.get("/pendientes/{padre_id}")
def obtener_pendientes(padre_id: str):
    try:
        # Obtener hijos del padre
        hijos = supabase.table("usuarios").select("id").eq("padre_id", padre_id).execute()
        if not hijos.data:
            return []

        hijos_ids = [h["id"] for h in hijos.data]

        # Obtener desafíos pendientes de validación
        pendientes = []
        for hijo_id in hijos_ids:
            response = supabase.table("desafios_completados").select("*").eq("hijo_id", hijo_id).eq("validado", False).neq("foto_url", None).execute()
            pendientes.extend(response.data)

        return pendientes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))