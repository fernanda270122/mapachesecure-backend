from fastapi import HTTPException
from app.database import supabase
import firebase_admin
from firebase_admin import credentials, messaging
import os

def _init_firebase():
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

def registrar_fcm_token(usuario_id: str, fcm_token: str):
    try:
        supabase.table("usuarios").update({"fcm_token": fcm_token}).eq("id", usuario_id).execute()
        return {"mensaje": "Token FCM registrado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
                title="MapacheSecure - App bloqueada",
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
