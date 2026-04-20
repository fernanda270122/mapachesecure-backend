from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers import usuarios, desafios, recompensas, apps, auth, ia

load_dotenv()

app = FastAPI(
    title="MapacheSecure API",
    description="Backend para el sistema de autorregulación digital MapacheSecure",
    version="1.0.0"
)

# Routers
app.include_router(usuarios.router)
app.include_router(desafios.router)
app.include_router(recompensas.router)
app.include_router(apps.router)
app.include_router(auth.router)
app.include_router(ia.router)

@app.get("/")
def root():
    return {
        "mensaje": "🦝 MapacheSecure API funcionando correctamente",
        "version": "1.0.0"
    }