from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date
from app.database import supabase 

router = APIRouter(
    prefix="/actividad",
    tags=["Actividad"]
)

class ActividadItem(BaseModel):
    package_name: str
    minutos_uso: int

class ReporteActividad(BaseModel):
    actividades: List[ActividadItem]


@router.post("/{hijo_id}")
def guardar_actividad_hijo(hijo_id: str, reporte: ReporteActividad):
    hoy = date.today().isoformat()
    
    for item in reporte.actividades:
        datos_actividad = {
            "hijo_id": hijo_id,
            "package_name": item.package_name,
            "minutos_uso": item.minutos_uso,
            "fecha": hoy
        }
        
        try:
            supabase.table("historial_actividad").upsert(
                datos_actividad, 
                on_conflict="hijo_id,package_name,fecha"
            ).execute()
        except Exception as e:
            print(f"❌ Error al guardar paquete {item.package_name}: {e}")
            
    return {"status": "success", "message": "Actividad actualizada correctamente"}


@router.get("/{hijo_id}")
def obtener_actividad_hijo(hijo_id: str):
    hoy = date.today().isoformat()
    
    try:
        respuesta = supabase.table("historial_actividad") \
            .select("package_name, minutos_uso") \
            .eq("hijo_id", hijo_id) \
            .eq("fecha", hoy) \
            .order("minutos_uso", desc=True) \
            .execute()
            
        return respuesta.data
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener el historial desde Supabase: {str(e)}"
        )
