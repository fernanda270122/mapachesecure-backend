from fastapi import HTTPException
from app.repositories import desafios_repo, usuarios_repo


def obtener_desafios():
    try:
        return desafios_repo.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def obtener_por_tipo(tipo: str):
    try:
        return desafios_repo.get_by_tipo(tipo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def completar_desafio(data):
      try:
          desafio = desafios_repo.get_by_id(data.desafio_id)
          if not desafio:
              raise HTTPException(status_code=404, detail="Desafío no encontrado")

          registro = {
              "hijo_id": data.hijo_id,
              "desafio_id": data.desafio_id,
              "foto_url": data.foto_url,
              "validado": False,
              "puntos_otorgados": 0
          }

          result = desafios_repo.registrar_completado(registro)
          return {
              "mensaje": "¡Desafío enviado al jefe! 🦝" ,
              "validado": False,
              "puntos_otorgados": 0,
              "data": result
          }
      except HTTPException:
          raise
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))

def obtener_completados(hijo_id: str):
    try:
        return desafios_repo.get_completados(hijo_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def obtener_puntos(hijo_id: str):
    try:
        data = desafios_repo.get_puntos(hijo_id)
        if not data:
            return {"hijo_id": hijo_id, "total_puntos": 0}
        return data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def validar_desafio(desafio_completado_id: str, aprobado: bool):
      try:
          registro = desafios_repo.get_completado_by_id(desafio_completado_id)
          if not registro:
              raise HTTPException(status_code=404, detail="Desafio no encontrado")

          dato = registro[0]

          if aprobado:
              desafio = desafios_repo.get_by_id(dato["desafio_id"])
              puntos = desafio[0]["puntos"]
              desafios_repo.actualizar_completado(desafio_completado_id, {"validado": True, "puntos_otorgados": puntos})
              desafios_repo.actualizar_estado(dato["desafio_id"], False)
              return {"mensaje": "Desafio aprobado! Puntos otorgados", "puntos_otorgados": puntos}
          else:
              desafios_repo.delete_completado(desafio_completado_id)
              return {"mensaje": "Desafio rechazado, el hijo puede reintentarlo", "puntos_otorgados": 0}
      except HTTPException:
          raise
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))

def obtener_pendientes(padre_id: str):
      try:
          hijos = usuarios_repo.get_hijos(padre_id)
          if not hijos:
              return []

          pendientes = []
          for hijo in hijos:
              rows = desafios_repo.get_pendientes_hijo(hijo["id"])
              for row in rows:
                  desafio = desafios_repo.get_by_id(row["desafio_id"])
                  row["titulo"] = desafio[0]["titulo"] if desafio else "Desafío"
                  row["hijo_nombre"] = hijo["nombre"]
                  row["url_evidencia"] = row.get("foto_url")
                  pendientes.append(row)
          return pendientes
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
    
def actualizar_estado(desafio_id, esta_activo: bool):
      try:
          return desafios_repo.actualizar_estado(desafio_id, esta_activo)
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))