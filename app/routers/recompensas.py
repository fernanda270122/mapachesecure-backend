from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services import recompensas_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/recompensas", tags=["Recompensas"])


class RecompensaCrear(BaseModel):
    padre_id: str
    hijo_id: str
    titulo: str
    costo_puntos: int

class CanjearRecompensa(BaseModel):
    hijo_id: str
    recompensa_id: str


@router.get("/{hijo_id}", dependencies=[Depends(get_current_user)])
def obtener_recompensas(hijo_id: str):
    return recompensas_service.obtener_recompensas(hijo_id)

@router.post("/", dependencies=[Depends(get_current_user)])
def crear_recompensa(recompensa: RecompensaCrear):
    return recompensas_service.crear_recompensa(recompensa)

@router.post("/canjear", dependencies=[Depends(get_current_user)])
def canjear_recompensa(data: CanjearRecompensa):
    return recompensas_service.canjear_recompensa(data)

@router.get("/historial/{hijo_id}", dependencies=[Depends(get_current_user)])
def historial_canjes(hijo_id: str):
    return recompensas_service.historial_canjes(hijo_id)

class CatalogoCrear(BaseModel):                                                                                                                                                                 
    nombre: str
    descripcion: str = ""
    puntos_sugeridos: int = 50
    icono: str = "🎁"


@router.get("/catalogo", dependencies=[Depends(get_current_user)])
def obtener_catalogo():
    return recompensas_service.obtener_catalogo()

@router.post("/catalogo", dependencies=[Depends(get_current_user)])
def agregar_al_catalogo(datos: CatalogoCrear, usuario=Depends(get_current_user)):
    return recompensas_service.agregar_al_catalogo(datos, usuario["id"])

@router.delete("/catalogo/{catalogo_id}", dependencies=[Depends(get_current_user)])
def eliminar_del_catalogo(catalogo_id: str, usuario=Depends(get_current_user)):
    return recompensas_service.eliminar_del_catalogo(catalogo_id, usuario["id"])