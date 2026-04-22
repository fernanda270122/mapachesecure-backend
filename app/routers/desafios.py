from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.services import desafios_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/desafios", tags=["Desafios"])


class DesafioCompletar(BaseModel):
    hijo_id: str
    desafio_id: str
    foto_url: Optional[str] = None


@router.get("/", dependencies=[Depends(get_current_user)])
def obtener_desafios():
    return desafios_service.obtener_desafios()

@router.get("/tipo/{tipo}", dependencies=[Depends(get_current_user)])
def obtener_por_tipo(tipo: str):
    return desafios_service.obtener_por_tipo(tipo)

@router.post("/completar", dependencies=[Depends(get_current_user)])
def completar_desafio(data: DesafioCompletar):
    return desafios_service.completar_desafio(data)

@router.get("/completados/{hijo_id}", dependencies=[Depends(get_current_user)])
def obtener_completados(hijo_id: str):
    return desafios_service.obtener_completados(hijo_id)

@router.get("/puntos/{hijo_id}", dependencies=[Depends(get_current_user)])
def obtener_puntos(hijo_id: str):
    return desafios_service.obtener_puntos(hijo_id)

@router.put("/validar/{desafio_completado_id}", dependencies=[Depends(get_current_user)])
def validar_desafio(desafio_completado_id: str, aprobado: bool):
    return desafios_service.validar_desafio(desafio_completado_id, aprobado)

@router.get("/pendientes/{padre_id}", dependencies=[Depends(get_current_user)])
def obtener_pendientes(padre_id: str):
    return desafios_service.obtener_pendientes(padre_id)
