from fastapi import APIRouter, Depends, HTTPException                                                                                                                                         
from pydantic import BaseModel
from typing import Literal                                                                                                                                                                    
from app.dependencies import get_current_user
from app.services import ia_service

class GenerarDesafiosRequest(BaseModel):                                                                                                                                                          
    categoria: Literal["cognitiva", "fisica", "hogar"]
    edad: int                                                                                                                                                                                     
    dificultad: Literal["facil", "medio", "dificil"]
    cantidad: int = 2

router = APIRouter(prefix="/ia", tags=["IA"])


@router.post("/generar", dependencies=[Depends(get_current_user)])                                                                                                                            
def generar_desafios(data: GenerarDesafiosRequest):
    try:                                                                                                                                                                                              
        resultado = ia_service.generar_desafios(
            categoria=data.categoria,
            edad=data.edad,
            dificultad=data.dificultad,
            cantidad=data.cantidad,
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar desafíos: {str(e)}")
