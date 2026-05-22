from fastapi import APIRouter, Depends, HTTPException                    
from pydantic import BaseModel
from typing import Optional, List
from app.dependencies import get_current_user
from app.database import supabase
import json

router = APIRouter(prefix="/bloqueos", tags=["bloqueos"])


class BloqueoCreate(BaseModel):
    tipo: str  # 'inmediato', 'horario', 'calendario', 'total'
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    package_names: Optional[str] = ""
    dias_semana: Optional[List[int]] = None
    fechas: Optional[str] = None

@router.post("/{hijo_id}")
def crear_bloqueo(hijo_id: str, bloqueo: BloqueoCreate, current_user=Depends(get_current_user)):
    if bloqueo.tipo in ("horario", "calendario"):
        if bloqueo.hora_inicio and bloqueo.hora_fin:
            try:
                # 🌟 SOLUCIÓN ULTRA SEGURA: Convertimos a minutos directos sin usar datetime.strptime
                h_inicio, m_inicio = map(int, bloqueo.hora_inicio.split(":"))
                h_fin, m_fin = map(int, bloqueo.hora_fin.split(":"))
                
                minutos_inicio = h_inicio * 60 + m_inicio
                minutos_fin = h_fin * 60 + m_fin
                
                # Calcular la diferencia tomando en cuenta si pasa de la medianoche
                diferencia_minutos = minutos_fin - minutos_inicio
                if diferencia_minutos < 0:
                    diferencia_minutos += 1440  # Sumamos los minutos de un día completo (24 * 60)
                
                # Validamos si es menor a 2 horas (120 minutos)
                if diferencia_minutos < 120:
                    raise HTTPException(status_code=400, detail="El bloqueo debe ser de mínimo 2 horas")
                    
            except Exception:
                raise HTTPException(status_code=400, detail="Formato de horarios inválido o corrupto")

    try:
        data = {
            "hijo_id": hijo_id,
            "tipo": bloqueo.tipo,
            "hora_inicio": bloqueo.hora_inicio,
            "hora_fin": bloqueo.hora_fin,
            "dias_semana": json.dumps(bloqueo.dias_semana) if bloqueo.dias_semana else None,
            "fechas": bloqueo.fechas if bloqueo.fechas else "",
            "package_names": bloqueo.package_names,
            "activo": True,
        }
        result = supabase.table("bloqueos_programados").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{hijo_id}")
def obtener_bloqueos(hijo_id: str, current_user=Depends(get_current_user)):
    result = supabase.table("bloqueos_programados").select("*").eq("hijo_id", hijo_id).execute()
    return result.data


@router.put("/{bloqueo_id}/desactivar")
def desactivar_bloqueo(bloqueo_id: str, current_user=Depends(get_current_user)):
    result = supabase.table("bloqueos_programados").update({"activo": False}).eq("id", bloqueo_id).execute()
    return result.data[0]


@router.delete("/{bloqueo_id}")
def eliminar_bloqueo(bloqueo_id: str, current_user=Depends(get_current_user)):
    supabase.table("bloqueos_programados").delete().eq("id", bloqueo_id).execute()
    return {"mensaje": "Bloqueo eliminado"}


@router.get("/{hijo_id}/apps-instante")
def obtener_apps_bloqueadas_instante(hijo_id: str, current_user=Depends(get_current_user)):
    """
    Este endpoint lo usará el Guardián en Flutter para saber qué apps 
    cerrar inmediatamente según la tabla 'apps_bloqueadas'.
    """
    try:
        result = supabase.table("apps_bloqueadas") \
            .select("package_name") \
            .eq("hijo_id", hijo_id) \
            .execute()
        
        return [item['package_name'] for item in result.data]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener apps: {str(e)}")
