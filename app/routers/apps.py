from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import supabase

router = APIRouter(prefix="/apps", tags=["Apps Bloqueadas"])

class AppBloqueadaCrear(BaseModel):
    hijo_id: str
    package_name: str  # ej: com.google.android.youtube
    nombre_app: str
    requiere_desafio: bool = True

# Obtener apps bloqueadas de un hijo
@router.get("/{hijo_id}")
def obtener_apps_bloqueadas(hijo_id: str):
    try:
        response = supabase.table("apps_bloqueadas").select("*").eq("hijo_id", hijo_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Agregar app bloqueada
@router.post("/")
def agregar_app_bloqueada(app: AppBloqueadaCrear):
    try:
        response = supabase.table("apps_bloqueadas").insert(app.model_dump()).execute()
        return {
            "mensaje": "App bloqueada agregada exitosamente",
            "data": response.data[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Eliminar app bloqueada
@router.delete("/{app_id}")
def eliminar_app_bloqueada(app_id: str):
    try:
        supabase.table("apps_bloqueadas").delete().eq("id", app_id).execute()
        return {"mensaje": "App desbloqueada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Verificar si una app está bloqueada para un hijo
@router.get("/verificar/{hijo_id}/{package_name}")
def verificar_app(hijo_id: str, package_name: str):
    try:
        response = supabase.table("apps_bloqueadas").select("*").eq("hijo_id", hijo_id).eq("package_name", package_name).execute()
        if response.data:
            return {
                "bloqueada": True,
                "requiere_desafio": response.data[0]["requiere_desafio"],
                "data": response.data[0]
            }
        return {"bloqueada": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))