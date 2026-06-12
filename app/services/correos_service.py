from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.repositories import correos_repo


def _hace_una_hora_iso():
    return (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()


def registrar_envio(tipo: str, email: str):
    # Nunca debe romper el flujo de registro o reset si falla el conteo
    try:
        correos_repo.registrar_evento(tipo, email)
    except Exception as e:
        print(f"[CUOTA_CORREOS] No se pudo registrar el envío: {e}")


def detectar_limite():
    # Al recibir el 429 de Supabase, los envíos exitosos de la última hora son el límite
    try:
        enviados = correos_repo.contar_eventos_desde(_hace_una_hora_iso())
        if enviados > 0:
            correos_repo.guardar_limite(enviados)
            return enviados
        return correos_repo.obtener_limite()
    except Exception as e:
        print(f"[CUOTA_CORREOS] No se pudo detectar el límite: {e}")
        return None


def estado_cuota():
    try:
        desde = _hace_una_hora_iso()
        enviados = correos_repo.contar_eventos_desde(desde)
        limite = correos_repo.obtener_limite()

        # El cupo más antiguo de la ventana se libera una hora después de usarse
        proximo_cupo = None
        primer_evento = correos_repo.primer_evento_desde(desde)
        if primer_evento:
            creado = datetime.fromisoformat(primer_evento.replace("Z", "+00:00"))
            proximo_cupo = (creado + timedelta(hours=1)).isoformat()

        return {
            "enviados_ultima_hora": enviados,
            "limite": limite,
            "limite_detectado": limite is not None,
            "restantes": max(limite - enviados, 0) if limite is not None else None,
            "proximo_cupo": proximo_cupo,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo consultar la cuota de correos: {e}")
