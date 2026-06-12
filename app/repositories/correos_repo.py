from app.database import supabase

LIMITE_CLAVE = "limite_correos_hora"


def registrar_evento(tipo: str, email: str):
    return supabase.table("correo_eventos").insert({"tipo": tipo, "email": email}).execute()

def contar_eventos_desde(desde_iso: str):
    res = supabase.table("correo_eventos").select("id", count="exact").gte("creado_en", desde_iso).execute()
    return res.count or 0

def primer_evento_desde(desde_iso: str):
    res = (
        supabase.table("correo_eventos")
        .select("creado_en")
        .gte("creado_en", desde_iso)
        .order("creado_en")
        .limit(1)
        .execute()
    )
    return res.data[0]["creado_en"] if res.data else None

def obtener_limite():
    res = supabase.table("correo_config").select("valor").eq("clave", LIMITE_CLAVE).execute()
    return res.data[0]["valor"] if res.data else None

def guardar_limite(valor: int):
    return supabase.table("correo_config").upsert({"clave": LIMITE_CLAVE, "valor": valor}).execute()
