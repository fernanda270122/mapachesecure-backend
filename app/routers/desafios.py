from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.services import desafios_service
from app.repositories import desafios_repo
from app.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException

class ActualizarEstadoRequest(BaseModel):
      id: str
      esta_activo: bool
      
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

@router.post("/actualizar_estado")
async def actualizar_estado(datos: dict):
    try:
        desafio_id = datos.get("id")
        nuevo_estado = datos.get("esta_activo")
        
        # Llamamos a la función del repo
        resultado = desafios_repo.actualizar_estado_desafio(desafio_id, nuevo_estado)
        
        return {"status": "success", "data": resultado.data}
    except Exception as e:
        # Importante tener el HTTPException importado arriba
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/actualizar_estado", dependencies=[Depends(get_current_user)])
def actualizar_estado(data: ActualizarEstadoRequest):
    return desafios_service.actualizar_estado(data.id, data.esta_activo)