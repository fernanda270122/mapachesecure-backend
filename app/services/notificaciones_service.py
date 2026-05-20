from fastapi import HTTPException
from app.database import supabase
import firebase_admin
from firebase_admin import credentials, messaging
import os

def _init_firebase():
    if not firebase_admin._apps:
        # Opción 1: JSON completo en variable de entorno (para Render)
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if cred_json:
            import json
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
        else:
            # Opción 2: ruta al archivo local (para desarrollo)
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
            cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

def registrar_fcm_token(usuario_id: str, fcm_token: str):
    try:
        supabase.table("usuarios").update({"fcm_token": fcm_token}).eq("id", usuario_id).execute()
        return {"mensaje": "Token FCM registrado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def enviar_notificacion_login(usuario_id: str, nombre: str, rol: str):
    """Envía una notificación push al dispositivo del usuario al iniciar sesión."""
    try:
        usuario = supabase.table("usuarios").select("fcm_token").eq("id", usuario_id).single().execute().data
        if not usuario or not usuario.get("fcm_token"):
            return {"mensaje": "No hay token FCM registrado para este usuario"}
        rol_texto = "Padre" if rol == "padre" else "Hijo"
        _init_firebase()
        message = messaging.Message(
            notification=messaging.Notification(
                title="Sesión iniciada — Raccu",
                body=f"Bienvenido, {nombre} ({rol_texto})",
            ),
            data={"tipo": "login", "usuario_id": usuario_id, "rol": rol},
            token=usuario["fcm_token"],
        )
        messaging.send(message)
        return {"mensaje": "Notificación de login enviada correctamente"}
    except Exception as e:
        return {"mensaje": f"Login exitoso (notificación no enviada: {str(e)})"}


def enviar_notificacion_padre(hijo_id: str, nombre_app: str):
    try:
        hijo = supabase.table("usuarios").select("nombre, padre_id").eq("id", hijo_id).single().execute().data
        if not hijo or not hijo.get("padre_id"):
            raise HTTPException(status_code=404, detail="Hijo o padre no encontrado")

        padre = supabase.table("usuarios").select("fcm_token, nombre").eq("id", hijo["padre_id"]).single().execute().data
        if not padre or not padre.get("fcm_token"):
            raise HTTPException(status_code=404, detail="El padre no tiene token FCM registrado")

        _init_firebase()
        message = messaging.Message(
            notification=messaging.Notification(
                title="Raccu - App bloqueada",
                body=f"{hijo['nombre']} intentó abrir {nombre_app}",
            ),
            data={"hijo_id": hijo_id, "app": nombre_app},
            token=padre["fcm_token"],
        )
        messaging.send(message)
        return {"mensaje": "Notificación enviada al padre"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def enviar_notificacion_evidencia(hijo_id: str, desafio_titulo: str):
    try:
        hijo = supabase.table("usuarios").select("nombre, padre_id").eq("id", hijo_id).single().execute().data
        if not hijo or not hijo.get("padre_id"):
            return
        padre = supabase.table("usuarios").select("fcm_token").eq("id", hijo["padre_id"]).single().execute().data
        if not padre or not padre.get("fcm_token"):
            return
        _init_firebase()
        message = messaging.Message(
            notification=messaging.Notification(
                title="Nueva evidencia de desafío 🦝" ,
                body=f"{hijo['nombre']} completó '{desafio_titulo}'. ¡Revisa la evidencia!",
            ),
            token=padre["fcm_token"],
        )
        messaging.send(message)
    except Exception:
        pass

def enviar_notificacion_validacion(hijo_id: str, aprobado: bool, desafio_titulo: str):
    try:
        hijo = supabase.table("usuarios").select("fcm_token").eq("id", hijo_id).single().execute().data
        if not hijo or not hijo.get("fcm_token"):
            return
        _init_firebase()
        titulo = "¡Desafío aprobado! 🎉" if aprobado else "Evidencia rechazada 💪"
        cuerpo = (
            f"Tu padre aprobó '{desafio_titulo}'. ¡Ganaste puntos!"
            if aprobado
            else f"Tu evidencia de '{desafio_titulo}' fue rechazada. ¡Inténtalo de nuevo!"
        )
        message = messaging.Message(
            notification=messaging.Notification(title=titulo, body=cuerpo),
            token=hijo["fcm_token"],
        )
        messaging.send(message)
    except Exception:
        pass