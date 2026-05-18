from app.repositories import canjes_repo, recompensas_repo

def obtener_pendientes(padre_id: str):
    return canjes_repo.obtener_canjes_pendientes(padre_id)

def tiene_pendiente_hijo(hijo_id: str):
    return {"tiene_pendiente": canjes_repo.tiene_pendiente(hijo_id)}

def aprobar_canje(canje_id: str):
    canje = canjes_repo.obtener_pendiente_de_hijo_por_id(canje_id)
    canjes_repo.actualizar_estado_canje(canje_id, "aprobado")
    if canje:
        recompensas_repo.deshabilitar_todas(canje["hijo_id"])

def rechazar_canje(canje_id: str):
    canjes_repo.actualizar_estado_canje(canje_id, "rechazado")