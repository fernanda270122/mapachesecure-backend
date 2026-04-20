from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services import desafios_service

router = APIRouter(prefix="/desafios", tags=["Desafios"])


class DesafioCompletar(BaseModel):
    hijo_id: str
    desafio_id: str
    foto_url: Optional[str] = None


@router.get("/")
def obtener_desafios():
    return desafios_service.obtener_desafios()

@router.get("/tipo/{tipo}")
def obtener_por_tipo(tipo: str):
    return desafios_service.obtener_por_tipo(tipo)

@router.post("/completar")
def completar_desafio(data: DesafioCompletar):
    return desafios_service.completar_desafio(data)

@router.get("/completados/{hijo_id}")
def obtener_completados(hijo_id: str):
    return desafios_service.obtener_completados(hijo_id)

@router.get("/puntos/{hijo_id}")
def obtener_puntos(hijo_id: str):
    return desafios_service.obtener_puntos(hijo_id)

@router.put("/validar/{desafio_completado_id}")
def validar_desafio(desafio_completado_id: str, aprobado: bool):
    return desafios_service.validar_desafio(desafio_completado_id, aprobado)

@router.get("/pendientes/{padre_id}")
def obtener_pendientes(padre_id: str):
    return desafios_service.obtener_pendientes(padre_id)
