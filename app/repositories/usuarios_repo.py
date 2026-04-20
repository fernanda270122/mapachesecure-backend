from app.database import supabase


def get_all():
    return supabase.table("usuarios").select("*").execute().data

def get_by_id(usuario_id: str):
    return supabase.table("usuarios").select("*").eq("id", usuario_id).execute().data

def create(datos: dict):
    return supabase.table("usuarios").insert(datos).execute().data[0]

def get_hijos(padre_id: str):
    return supabase.table("usuarios").select("*").eq("padre_id", padre_id).execute().data

def update(usuario_id: str, datos: dict):
    return supabase.table("usuarios").update(datos).eq("id", usuario_id).execute().data
