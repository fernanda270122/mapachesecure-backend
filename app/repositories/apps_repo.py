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
