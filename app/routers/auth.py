from fastapi import APIRouter
from pydantic import BaseModel
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticacion"])


class RegistroRequest(BaseModel):
    email: str
    password: str
    nombre: str
    rol: str

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/registro")
def registro(data: RegistroRequest):
    return auth_service.registro(data)

@router.post("/login")
def login(data: LoginRequest):
    return auth_service.login(data)

@router.post("/logout")
def logout():
    return auth_service.logout()

@router.put("/vincular-hijo")
def vincular_hijo(hijo_id: str, padre_id: str):
    return auth_service.vincular_hijo(hijo_id, padre_id)
