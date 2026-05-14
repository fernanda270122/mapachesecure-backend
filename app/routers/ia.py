from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from app.dependencies import get_current_user
from app.services import ia_service
from app.repositories import usuarios_repo

class GenerarDesafiosRequest(BaseModel):
    categoria: Literal["cognitiva", "fisica", "hogar"]
    hijo_id: str
    dificultad: Literal["facil", "medio", "dificil"]
    cantidad: int = 3

router = APIRouter(prefix="/ia", tags=["IA"])


@router.post("/generar", dependencies=[Depends(get_current_user)])
def generar_desafios(data: GenerarDesafiosRequest):
    try:
        hijo = usuarios_repo.get_by_id(data.hijo_id)
        if not hijo:
            raise HTTPException(status_code=404, detail="Hijo no encontrado")
        hijo = hijo[0]
        resultado = ia_service.generar_desafios(
            categoria=data.categoria,
            edad=hijo.get("edad"),
            dificultad=data.dificultad,
            cantidad=data.cantidad,
            sexo=hijo.get("sexo"),
            nivel_escolar=hijo.get("nivel_escolar"),
            intereses=hijo.get("intereses"),
            personalidad=hijo.get("personalidad"),
        )
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar desafíos: {str(e)}")

class AsignarDesafioRequest(BaseModel):
      titulo: str
      descripcion: str
      puntos: int
      tipo: str
      dificultad: str
      hijo_id: str
      esta_activo: bool = False
      
@router.post("/asignar", dependencies=[Depends(get_current_user)])
def asignar_desafio(data: AsignarDesafioRequest):
    try:
        from app.repositories import desafios_repo
        resultado = desafios_repo.insertar({
            "titulo": data.titulo,
            "descripcion": data.descripcion,
            "puntos": data.puntos,
            "tipo": data.tipo,
            "dificultad": data.dificultad,
            "hijo_id": data.hijo_id,
            "esta_activo": data.esta_activo,
        })
        return {"mensaje": "Desafío asignado correctamente", "data": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))