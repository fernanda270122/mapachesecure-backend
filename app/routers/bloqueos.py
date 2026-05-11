from fastapi import APIRouter, Depends, HTTPException                                                                                                                                       
from pydantic import BaseModel
from typing import Optional, List
from app.dependencies import get_current_user
from app.database import supabase
import json

router = APIRouter(prefix="/bloqueos", tags=["bloqueos"])


class BloqueoCreate(BaseModel):
    tipo: str  # 'inmediato', 'horario', 'calendario'
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    dias_semana: Optional[List[int]] = None
    fechas: Optional[str] = None

@router.post("/{hijo_id}")
def crear_bloqueo(hijo_id: str, bloqueo: BloqueoCreate, current_user=Depends(get_current_user)):
    if bloqueo.tipo in ("horario", "calendario"):
        if bloqueo.hora_inicio and bloqueo.hora_fin:
            from datetime import datetime
            inicio = datetime.strptime(bloqueo.hora_inicio, "%H:%M")
            fin = datetime.strptime(bloqueo.hora_fin, "%H:%M")
            diferencia = (fin - inicio).seconds / 3600
            if diferencia < 2:
                raise HTTPException(status_code=400, detail="El bloqueo debe ser de mínimo 2 horas")

    data = {
        "hijo_id": hijo_id,
        "tipo": bloqueo.tipo,
        "hora_inicio": bloqueo.hora_inicio,
        "hora_fin": bloqueo.hora_fin,
        "dias_semana": json.dumps(bloqueo.dias_semana) if bloqueo.dias_semana else None,
        "fechas": bloqueo.fechas,
        "activo": True,
    }
    result = supabase.table("bloqueos_programados").insert(data).execute()
    return result.data[0]


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