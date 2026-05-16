from fastapi import HTTPException
from app.repositories import auth_repo


def registro(data):
    try:
        auth_response = auth_repo.sign_up(data.email, data.password)
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Error al crear usuario")

        perfil = {"id": auth_response.user.id, "email": data.email, "nombre": data.nombre, "rol": data.rol}
        auth_repo.create_perfil(perfil)

        return {
            "mensaje": "Usuario registrado exitosamente",
            "user_id": auth_response.user.id,
            "email": data.email,
            "nombre": data.nombre,
            "rol": data.rol
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def login(data):
    try:
        auth_response = auth_repo.sign_in(data.email, data.password)
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        perfil = auth_repo.get_perfil(auth_response.user.id)
        return {
            "mensaje": "Login exitoso",
            "access_token": auth_response.session.access_token,
            "user_id": auth_response.user.id,
            "perfil": perfil[0] if perfil else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def logout():
    try:
        auth_repo.sign_out()
        return {"mensaje": "Sesion cerrada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def vincular_hijo(hijo_id: str, padre_id: str):
    try:
        data = auth_repo.vincular_hijo(hijo_id, padre_id)
        if not data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"mensaje": "Hijo vinculado al padre exitosamente", "data": data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def registro_hijo(data, padre_id: str):
    try:
        auth_response = auth_repo.sign_up(data.email, data.password)
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Error al crear cuenta del hijo")

        perfil = {
            "id": auth_response.user.id,
            "email": data.email,
            "nombre": data.nombre,
            "rol": "hijo",
            "padre_id": padre_id,
            "edad": data.edad
        }
        auth_repo.create_perfil(perfil)
        
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": [data.email],
            "subject": "¡Bienvenido a ! DRaccuescarga la app 🦝" ,
            "html": f"""
                <h2>¡Hola {data.nombre}!</h2>
                <p>Tu cuenta en Raccu ya está lista.</p>
                <p>Descarga la app en tu celular haciendo clic aquí:</p>
                <a href="https://drive.google.com/uc?export=download&id=165E8JxUPEHuUICXvlcBvoFHlkjMreR8c"
                    style="background:#6200EA;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">
                    Descargar Raccu
                </a>
                <p>Una vez descargada, instálala y entra con tu correo y contraseña.</p>
                <p>¡Nos vemos adentro! 🦝</p>
            """
        })

        return {
            "mensaje": "Hijo registrado exitosamente",
            "user_id": auth_response.user.id,
            "nombre": data.nombre,
            "padre_id": padre_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def recuperar_password(email: str):
    try:
        auth_repo.reset_password(email)
        return{"mensaje": "Correo de recuperación enviado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def cambiar_password(access_token: str, nueva_password: str):
    try:
        auth_repo.cambiar_password(access_token, nueva_password)
        return {"mensaje": "Contraseña actualizada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#ENVIO DE IMAGENES PARA CONFIRMAR IDENTIDAD
import resend
import os
from app.database import supabase

async def verificar_identidad(user_id: str, nombre: str, email: str, foto):
      try:
          print(f"[VERIFICAR] Recibiendo foto para user_id={user_id}")
          contenido = await foto.read()
          print(f"[VERIFICAR] Foto leída, tamaño={len(contenido)} bytes")

          ruta = f"verificaciones/{user_id}.jpg"
          supabase.storage.from_("verificaciones").upload(ruta, contenido, {"content-type": "image/jpeg"})
          print(f"[VERIFICAR] Foto subida a Supabase: {ruta}")

          foto_url = supabase.storage.from_("verificaciones").get_public_url(ruta)
          print(f"[VERIFICAR] URL pública: {foto_url}")

          resend.api_key = os.getenv("RESEND_API_KEY")
          print(f"[VERIFICAR] RESEND_API_KEY cargada: {'sí' if resend.api_key else 'NO'}")

          resend.Emails.send({
              "from": "onboarding@resend.dev",
              "to": ["raccucavy@gmail.com"],
              "subject": f"Verificación de identidad: {nombre}",
              "html": f"""
                  <h2>Nueva solicitud de verificación</h2>
                  <p><b>Nombre:</b> {nombre}</p>
                  <p><b>Email:</b> {email}</p>
                  <p><b>User ID:</b> {user_id}</p>
                  <p><a href="{foto_url}">Ver foto de identificación</a></p>
              """
          })
          print(f"[VERIFICAR] Email enviado correctamente")

          return {"mensaje": "Verificación enviada, pronto revisaremos tu solicitud."}
      except Exception as e:
          print(f"[VERIFICAR] ERROR: {str(e)}")
          raise HTTPException(status_code=500, detail=str(e))