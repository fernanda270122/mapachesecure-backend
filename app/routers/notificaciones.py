from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services import notificaciones_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


class FCMTokenRequest(BaseModel):
    fcm_token: str

class NotificacionRequest(BaseModel):
    hijo_id: str
    nombre_app: str


@router.post("/token")
def registrar_token(data: FCMTokenRequest, current_user=Depends(get_current_user)):
    return notificaciones_service.registrar_fcm_token(current_user.id, data.fcm_token)

@router.post("/app-bloqueada")
def notificar_app_bloqueada(data: NotificacionRequest, current_user=Depends(get_current_user)):
    return notificaciones_service.enviar_notificacion_padre(data.hijo_id, data.nombre_app)
