from app.database import supabase

def obtener_canjes_pendientes(padre_id: str):
    hijos = supabase.table("usuarios").select("id").eq("padre_id", padre_id).execute()
    hijo_ids = [h["id"] for h in hijos.data]
    if not hijo_ids:
        return []
    result = supabase.table("canjes").select("*, recompensas(titulo), usuarios(nombre, sexo)").in_("hijo_id", hijo_ids).eq("estado", "pendiente").execute()
    return result.data

def tiene_pendiente(hijo_id: str) -> bool:
    result = supabase.table("canjes").select("id").eq("hijo_id", hijo_id).eq("estado", "pendiente").execute()
    return len(result.data) > 0

def obtener_pendiente_de_hijo_por_id(canje_id: str):
    result = supabase.table("canjes").select("*").eq("id", canje_id).execute()
    return result.data[0] if result.data else None

def actualizar_estado_canje(canje_id: str, estado: str):
    supabase.table("canjes").update({"estado": estado}).eq("id", canje_id).execute()