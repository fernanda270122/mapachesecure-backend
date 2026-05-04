from app.database import supabase


def get_by_hijo(hijo_id: str):
    return supabase.table("recompensas").select("*").eq("hijo_id", hijo_id).eq("disponible", True).execute().data

def create(datos: dict):
    return supabase.table("recompensas").insert(datos).execute().data[0]

def get_by_id(recompensa_id: str):
    return supabase.table("recompensas").select("*").eq("id", recompensa_id).execute().data

def registrar_canje(datos: dict):
    return supabase.table("canjes").insert(datos).execute().data[0]

def get_historial_canjes(hijo_id: str):
    return supabase.table("canjes").select("*").eq("hijo_id", hijo_id).execute().data

def get_catalogo():
    return supabase.table("catalogo_recompensas").select("*").execute().data

def create_catalogo(datos: dict):
    return supabase.table("catalogo_recompensas").insert(datos).execute().data