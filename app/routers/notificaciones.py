from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ia_service import generar_desafios

router = APIRouter(prefix="/ia", tags=["IA"])

class SolicitudDesafios(BaseModel):
    categoria: str
    edad: int
    dificultad: str
    cantidad: int = 2

@router.post("/generar-desafios")
def generar(solicitud: SolicitudDesafios):
    categorias_validas = ["cognitiva", "fisica", "hogar"]
    dificultades_validas = ["facil", "medio", "dificil"]

    if solicitud.categoria not in categorias_validas:
        raise HTTPException(status_code=400, detail=f"Categoría inválida. Usa: {categorias_validas}")
    if solicitud.dificultad not in dificultades_validas:
        raise HTTPException(status_code=400, detail=f"Dificultad inválida. Usa: {dificultades_validas}")

    resultado = generar_desafios(
        categoria=solicitud.categoria,
        edad=solicitud.edad,
        dificultad=solicitud.dificultad,
        cantidad=solicitud.cantidad
    )
    return resultado