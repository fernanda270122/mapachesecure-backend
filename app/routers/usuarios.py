from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import supabase
from typing import Optional

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Modelos
class UsuarioCrear(BaseModel):
    nombre: str
    email: Optional[str] = None
    rol: str  # 'padre' o 'hijo'
    padre_id: Optional[str] = None
    edad: Optional[int] = None

# Obtener todos los usuarios
@router.get("/")
def obtener_usuarios():
    try:
        response = supabase.table("usuarios").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener usuario por ID
@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: str):
    try:
        response = supabase.table("usuarios").select("*").eq("id", usuario_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Crear usuario
@router.post("/")
def crear_usuario(usuario: UsuarioCrear):
    try:
        # Eliminar campos None antes de enviar a Supabase
        datos = {k: v for k, v in usuario.model_dump().items() if v is not None}
        response = supabase.table("usuarios").insert(datos).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener hijos de un padre
@router.get("/{padre_id}/hijos")
def obtener_hijos(padre_id: str):
    try:
        response = supabase.table("usuarios").select("*").eq("padre_id", padre_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    