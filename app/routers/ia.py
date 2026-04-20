from fastapi import APIRouter

router = APIRouter(prefix="/ia", tags=["IA"])


@router.get("/")
def ia_status():
    return {"mensaje": "Módulo de IA MapacheSecure - próximamente"}
