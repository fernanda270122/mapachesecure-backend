from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.services import usuarios_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


class UsuarioCrear(BaseModel):
    nombre: str
    email: Optional[str] = None
    rol: str
    padre_id: Optional[str] = None
    edad: Optional[int] = None


@router.get("/", dependencies=[Depends(get_current_user)])
def obtener_usuarios():
    return usuarios_service.obtener_usuarios()

@router.get("/{usuario_id}", dependencies=[Depends(get_current_user)])
def obtener_usuario(usuario_id: str):
    return usuarios_service.obtener_usuario(usuario_id)

@router.post("/", dependencies=[Depends(get_current_user)])
def crear_usuario(usuario: UsuarioCrear):
    return usuarios_service.crear_usuario(usuario)

@router.get("/{padre_id}/hijos", dependencies=[Depends(get_current_user)])
def obtener_hijos(padre_id: str):
    return usuarios_service.obtener_hijos(padre_id)
