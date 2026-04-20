from app.database import supabase


def sign_up(email: str, password: str):
    return supabase.auth.sign_up({"email": email, "password": password})

def sign_in(email: str, password: str):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def sign_out():
    supabase.auth.sign_out()

def create_perfil(perfil: dict):
    return supabase.table("usuarios").insert(perfil).execute()

def get_perfil(usuario_id: str):
    return supabase.table("usuarios").select("*").eq("id", usuario_id).execute().data

def vincular_hijo(hijo_id: str, padre_id: str):
    return supabase.table("usuarios").update({"padre_id": padre_id}).eq("id", hijo_id).execute().data
