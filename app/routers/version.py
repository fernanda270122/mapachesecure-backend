from fastapi import APIRouter

router = APIRouter()

@router.get("/version")
def obtener_version():
    return {
        "version": "1.1",
        "url": "https://drive.google.com/uc?export=download&id=165E8JxUPEHuUICXvlcBvoFHlkjMreR8c"
    }