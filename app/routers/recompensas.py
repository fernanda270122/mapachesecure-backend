from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import supabase

router = APIRouter(prefix="/recompensas", tags=["Recompensas"])

# Modelos
class RecompensaCrear(BaseModel):
    padre_id: str
    hijo_id: str
    titulo: str
    costo_puntos: int

class CanjearRecompensa(BaseModel):
    hijo_id: str
    recompensa_id: str

# Obtener recompensas de un hijo
@router.get("/{hijo_id}")
def obtener_recompensas(hijo_id: str):
    try:
        response = supabase.table("recompensas").select("*").eq("hijo_id", hijo_id).eq("disponible", True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Crear recompensa (el padre la configura)
@router.post("/")
def crear_recompensa(recompensa: RecompensaCrear):
    try:
        response = supabase.table("recompensas").insert(recompensa.model_dump()).execute()
        return {
            "mensaje": "Recompensa creada exitosamente 🎁",
            "data": response.data[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Canjear recompensa
@router.post("/canjear")
def canjear_recompensa(data: CanjearRecompensa):
    try:
        # Obtener la recompensa
        recompensa = supabase.table("recompensas").select("*").eq("id", data.recompensa_id).execute()
        if not recompensa.data:
            raise HTTPException(status_code=404, detail="Recompensa no encontrada")
        
        costo = recompensa.data[0]["costo_puntos"]

        # Verificar puntos del hijo
        puntos_data = supabase.table("puntos_por_hijo").select("*").eq("hijo_id", data.hijo_id).execute()
        puntos_actuales = puntos_data.data[0]["total_puntos"] if puntos_data.data else 0

        if puntos_actuales < costo:
            return {
                "mensaje": "No tienes suficientes puntos 😢",
                "puntos_actuales": puntos_actuales,
                "puntos_necesarios": costo
            }

        # Registrar el canje
        canje = {
            "hijo_id": data.hijo_id,
            "recompensa_id": data.recompensa_id
        }
        supabase.table("canjes").insert(canje).execute()

        return {
            "mensaje": "¡Recompensa canjeada exitosamente! 🦝🎉",
            "puntos_gastados": costo,
            "puntos_restantes": puntos_actuales - costo
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener historial de canjes de un hijo
@router.get("/historial/{hijo_id}")
def historial_canjes(hijo_id: str):
    try:
        response = supabase.table("canjes").select("*").eq("hijo_id", hijo_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))