from fastapi import APIRouter
from pydantic import BaseModel
from app.services import apps_service

router = APIRouter(prefix="/apps", tags=["Apps Bloqueadas"])


class AppBloqueadaCrear(BaseModel):
    hijo_id: str
    package_name: str
    nombre_app: str
    requiere_desafio: bool = True


@router.get("/{hijo_id}")
def obtener_apps_bloqueadas(hijo_id: str):
    return apps_service.obtener_apps_bloqueadas(hijo_id)

@router.post("/")
def agregar_app_bloqueada(app: AppBloqueadaCrear):
    return apps_service.agregar_app_bloqueada(app)

@router.delete("/{app_id}")
def eliminar_app_bloqueada(app_id: str):
    return apps_service.eliminar_app_bloqueada(app_id)

@router.get("/verificar/{hijo_id}/{package_name}")
def verificar_app(hijo_id: str, package_name: str):
    return apps_service.verificar_app(hijo_id, package_name)
