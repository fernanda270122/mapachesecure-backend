from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import supabase

router = APIRouter(prefix="/auth", tags=["Autenticacion"])

class RegistroRequest(BaseModel):
    email: str
    password: str
    nombre: str
    rol: str  # 'padre' o 'hijo'

class LoginRequest(BaseModel):
    email: str
    password: str

# Registro
@router.post("/registro")
def registro(data: RegistroRequest):
    try:
        # Crear usuario en Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Error al crear usuario")

        # Crear perfil en tabla usuarios
        perfil = {
            "id": auth_response.user.id,
            "email": data.email,
            "nombre": data.nombre,
            "rol": data.rol
        }
        supabase.table("usuarios").insert(perfil).execute()

        return {
            "mensaje": "Usuario registrado exitosamente",
            "user_id": auth_response.user.id,
            "email": data.email,
            "nombre": data.nombre,
            "rol": data.rol
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Login
@router.post("/login")
def login(data: LoginRequest):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        # Obtener perfil del usuario
        perfil = supabase.table("usuarios").select("*").eq("id", auth_response.user.id).execute()

        return {
            "mensaje": "Login exitoso",
            "access_token": auth_response.session.access_token,
            "user_id": auth_response.user.id,
            "perfil": perfil.data[0] if perfil.data else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Logout
@router.post("/logout")
def logout():
    try:
        supabase.auth.sign_out()
        return {"mensaje": "Sesion cerrada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vincular hijo con padre
@router.put("/vincular-hijo")
def vincular_hijo(hijo_id: str, padre_id: str):
    try:
        response = supabase.table("usuarios").update({
            "padre_id": padre_id
        }).eq("id", hijo_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {
            "mensaje": "Hijo vinculado al padre exitosamente",
            "data": response.data[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))