from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services import auth_service
from app.dependencies import get_current_user
from typing import Optional
import resend
import os
from fastapi import UploadFile, File, Form
  
router = APIRouter(prefix="/auth", tags=["Autenticacion"])


class RegistroRequest(BaseModel):
    email: str
    password: str
    nombre: str
    rol: str

class LoginRequest(BaseModel):
    email: str
    password: str
    
class RegistroHijoRequest(BaseModel):                                                                                                                                                           
    nombre: str
    email: str
    password: str
    edad: Optional[int] = None



@router.post("/registro")
def registro(data: RegistroRequest):
    return auth_service.registro(data)

@router.post("/login")
def login(data: LoginRequest):
    return auth_service.login(data)

@router.post("/logout", dependencies=[Depends(get_current_user)])
def logout():
    return auth_service.logout()

@router.put("/vincular-hijo", dependencies=[Depends(get_current_user)])
def vincular_hijo(hijo_id: str, padre_id: str):
    return auth_service.vincular_hijo(hijo_id, padre_id)

@router.post("/registro-hijo", dependencies=[Depends(get_current_user)])
def registro_hijo(data: RegistroHijoRequest, current_user=Depends(get_current_user)):
    return auth_service.registro_hijo(data, current_user.id)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh(data: RefreshTokenRequest):
    return auth_service.refresh_token(data.refresh_token)

class RecuperarPasswordRequest(BaseModel):
    email: str
@router.post("/recuperar-password")
def recuperar_password(data: RecuperarPasswordRequest):
    return auth_service.recuperar_password(data.email)

class CambiarPasswordRequest(BaseModel):
    access_token: str
    nueva_password: str
@router.post("/cambiar-password")
def cambiar_password(data: CambiarPasswordRequest):
    return auth_service.cambiar_password(data.access_token, data.nueva_password)

#envio de fotos para confirmar identidad
@router.post("/verificar-identidad")
async def verificar_identidad(
    user_id: str = Form(...),
    nombre: str = Form(...),
    email: str = Form(...),
    foto: UploadFile = File(...)
):
    return await auth_service.verificar_identidad(user_id, nombre, email, foto)
