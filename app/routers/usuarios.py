from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services import usuarios_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


class UsuarioCrear(BaseModel):
    nombre: str
    email: Optional[str] = None
    rol: str
    padre_id: Optional[str] = None
    edad: Optional[int] = None


@router.get("/")
def obtener_usuarios():
    return usuarios_service.obtener_usuarios()

@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: str):
    return usuarios_service.obtener_usuario(usuario_id)

@router.post("/")
def crear_usuario(usuario: UsuarioCrear):
    return usuarios_service.crear_usuario(usuario)

@router.get("/{padre_id}/hijos")
def obtener_hijos(padre_id: str):
    return usuarios_service.obtener_hijos(padre_id)
