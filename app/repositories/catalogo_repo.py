from app.database import supabase


def get_all():
    return supabase.table("catalogo_recompensas").select("*").order("created_at").execute().data

def create(datos: dict):
    return supabase.table("catalogo_recompensas").insert(datos).execute().data[0]

def get_by_id(catalogo_id: str):
    return supabase.table("catalogo_recompensas").select("*").eq("id", catalogo_id).execute().data

def delete(catalogo_id: str, padre_id: str):
    return supabase.table("catalogo_recompensas").delete().eq("id", catalogo_id).eq("creado_por", padre_id).execute().data