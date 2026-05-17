from app.repositories import canjes_repo

def obtener_pendientes(padre_id: str):
    return canjes_repo.obtener_canjes_pendientes(padre_id)

def aprobar_canje(canje_id: str):
    canjes_repo.actualizar_estado_canje(canje_id, "aprobado")

def rechazar_canje(canje_id: str):
    canjes_repo.actualizar_estado_canje(canje_id, "rechazado")