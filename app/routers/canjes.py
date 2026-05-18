from fastapi import APIRouter
from app.services import canjes_service

router = APIRouter(prefix="/canjes", tags=["canjes"])

@router.get("/pendientes/{padre_id}")
def get_pendientes(padre_id: str):
    return canjes_service.obtener_pendientes(padre_id)

@router.get("/tiene-pendiente/{hijo_id}")
def get_tiene_pendiente(hijo_id: str):
    return canjes_service.tiene_pendiente_hijo(hijo_id)

@router.post("/aprobar/{canje_id}")
def aprobar(canje_id: str):
    canjes_service.aprobar_canje(canje_id)
    return {"mensaje": "Canje aprobado"}

@router.post("/rechazar/{canje_id}")
def rechazar(canje_id: str):
    canjes_service.rechazar_canje(canje_id)
    return {"mensaje": "Canje rechazado"}