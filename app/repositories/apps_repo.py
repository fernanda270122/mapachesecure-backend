from app.database import supabase


def get_by_hijo(hijo_id: str):
    return supabase.table("apps_bloqueadas").select("*").eq("hijo_id", hijo_id).execute().data

def create(datos: dict):
    return supabase.table("apps_bloqueadas").insert(datos).execute().data[0]

def delete(app_id: str):
    supabase.table("apps_bloqueadas").delete().eq("id", app_id).execute()

def get_by_hijo_y_package(hijo_id: str, package_name: str):
    return (
        supabase.table("apps_bloqueadas")
        .select("*")
        .eq("hijo_id", hijo_id)
        .eq("package_name", package_name)
        .execute()
        .data
    )
def get_uso_hoy(hijo_id: str, fecha: str):
    return (
        supabase.table("uso_diario")
        .select("*")
        .eq("hijo_id", hijo_id)
        .eq("fecha", fecha)
        .execute()
        .data
    )

def crear_uso(datos: dict):
    return supabase.table("uso_diario").insert(datos).execute().data[0]

def actualizar_uso(uso_id: str, minutos: int):
    return supabase.table("uso_diario").update({"minutos_usados": minutos}).eq("id", uso_id).execute().data