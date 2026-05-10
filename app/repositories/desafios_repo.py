from app.database import supabase


def get_all():
    return supabase.table("desafios").select("*").execute().data

def get_by_tipo(tipo: str):
    return supabase.table("desafios").select("*").eq("tipo", tipo).execute().data

def get_by_id(desafio_id: str):
    return supabase.table("desafios").select("*").eq("id", desafio_id).execute().data

def registrar_completado(registro: dict):
    return supabase.table("desafios_completados").insert(registro).execute().data[0]

def get_completados(hijo_id: str):
    return supabase.table("desafios_completados").select("*").eq("hijo_id", hijo_id).execute().data

def get_puntos(hijo_id: str):
    return supabase.table("puntos_por_hijo").select("*").eq("hijo_id", hijo_id).execute().data

def get_completado_by_id(desafio_completado_id: str):
    return supabase.table("desafios_completados").select("*").eq("id", desafio_completado_id).execute().data

def actualizar_completado(desafio_completado_id: str, datos: dict):
    return supabase.table("desafios_completados").update(datos).eq("id", desafio_completado_id).execute().data

def get_pendientes_hijo(hijo_id: str):
    return (
        supabase.table("desafios_completados")
        .select("*")
        .eq("hijo_id", hijo_id)
        .eq("validado", False)
        .neq("foto_url", None)
        .execute()
        .data
    )
