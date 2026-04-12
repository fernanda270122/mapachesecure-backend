from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers import usuarios, desafios, recompensas

load_dotenv()

app = FastAPI(
    title="MapacheSecure API",
    description="Backend para el sistema de autorregulacion digital MapacheSecure",
    version="1.0.0"
)

app.include_router(usuarios.router)
app.include_router(desafios.router)
app.include_router(recompensas.router)

@app.get("/")
def root():
    return {
        "mensaje": "MapacheSecure API funcionando correctamente",
        "version": "1.0.0"
    }