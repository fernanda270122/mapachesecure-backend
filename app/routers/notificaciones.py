from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.notificaciones_service import registrar_fcm_token, enviar_notificacion_login
from app.dependencies import get_current_user

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


class TokenFCMRequest(BaseModel):
    fcm_token: str


class LoginNotificacionRequest(BaseModel):
    nombre: str
    rol: str


@router.post("/token")
def guardar_token(body: TokenFCMRequest, usuario_id: str = Depends(get_current_user)):
    """Guarda el token FCM del dispositivo del usuario para poder enviarle notificaciones push."""
    return registrar_fcm_token(usuario_id, body.fcm_token)


@router.post("/login")
def notificar_login(body: LoginNotificacionRequest, usuario_id: str = Depends(get_current_user)):
    """Envía una notificación push al dispositivo del usuario confirmando el inicio de sesión."""
    return enviar_notificacion_login(usuario_id, body.nombre, body.rol)
