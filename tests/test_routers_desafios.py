from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user


def _fake_user():
    u = MagicMock()
    u.id = "uid-test"
    return u


app.dependency_overrides[get_current_user] = _fake_user
client = TestClient(app)

_HEADERS = {"Authorization": "Bearer token-test"}
_DESAFIO = {"id": "d1", "titulo": "Reto", "puntos": 10}


class TestObtenerDesafiosRouter:
    def test_devuelve_lista(self):
        with patch("app.routers.desafios.desafios_service.obtener_desafios", return_value=[_DESAFIO]):
            r = client.get("/desafios/", headers=_HEADERS)
            assert r.status_code == 200

    def test_error_500(self):
        with patch("app.routers.desafios.desafios_service.obtener_desafios", side_effect=HTTPException(500, "fallo")):
            r = client.get("/desafios/", headers=_HEADERS)
            assert r.status_code == 500


class TestObtenerPorTipoRouter:
    def test_devuelve_por_tipo(self):
        with patch("app.routers.desafios.desafios_service.obtener_por_tipo", return_value=[_DESAFIO]):
            r = client.get("/desafios/tipo/cognitivo", headers=_HEADERS)
            assert r.status_code == 200


class TestCompletarDesafioRouter:
    def test_completa_exitosamente(self):
        with patch("app.routers.desafios.desafios_service.completar_desafio", return_value={"mensaje": "ok"}):
            r = client.post("/desafios/completar", headers=_HEADERS, json={
                "hijo_id": "h1", "desafio_id": "d1", "foto_url": None
            })
            assert r.status_code == 200

    def test_desafio_no_encontrado(self):
        with patch("app.routers.desafios.desafios_service.completar_desafio", side_effect=HTTPException(404, "no existe")):
            r = client.post("/desafios/completar", headers=_HEADERS, json={
                "hijo_id": "h1", "desafio_id": "fantasma", "foto_url": None
            })
            assert r.status_code == 404


class TestObtenerPorHijoRouter:
    def test_devuelve_desafios_del_hijo(self):
        with patch("app.routers.desafios.desafios_repo.get_by_hijo", return_value=[_DESAFIO]):
            r = client.get("/desafios/hijo/h1", headers=_HEADERS)
            assert r.status_code == 200


class TestObtenerCompletadosRouter:
    def test_devuelve_completados(self):
        with patch("app.routers.desafios.desafios_service.obtener_completados", return_value=[]):
            r = client.get("/desafios/completados/h1", headers=_HEADERS)
            assert r.status_code == 200


class TestObtenerPuntosRouter:
    def test_devuelve_puntos(self):
        with patch("app.routers.desafios.desafios_service.obtener_puntos", return_value={"total": 50}):
            r = client.get("/desafios/puntos/h1", headers=_HEADERS)
            assert r.status_code == 200


class TestValidarDesafioRouter:
    def test_aprueba_desafio(self):
        with patch("app.routers.desafios.desafios_service.validar_desafio", return_value={"mensaje": "aprobado"}):
            r = client.put("/desafios/validar/dc1?aprobado=true", headers=_HEADERS)
            assert r.status_code == 200

    def test_rechaza_desafio(self):
        with patch("app.routers.desafios.desafios_service.validar_desafio", return_value={"mensaje": "rechazado"}):
            r = client.put("/desafios/validar/dc1?aprobado=false", headers=_HEADERS)
            assert r.status_code == 200

    def test_no_encontrado(self):
        with patch("app.routers.desafios.desafios_service.validar_desafio", side_effect=HTTPException(404, "no existe")):
            r = client.put("/desafios/validar/x?aprobado=true", headers=_HEADERS)
            assert r.status_code == 404


class TestObtenerPendientesRouter:
    def test_devuelve_pendientes(self):
        with patch("app.routers.desafios.desafios_service.obtener_pendientes", return_value=[]):
            r = client.get("/desafios/pendientes/p1", headers=_HEADERS)
            assert r.status_code == 200


class TestActualizarEstadoRouter:
    def test_actualiza_estado(self):
        with patch("app.routers.desafios.desafios_service.actualizar_estado", return_value={"ok": True}):
            r = client.post("/desafios/actualizar_estado", headers=_HEADERS, json={"id": "d1", "esta_activo": True})
            assert r.status_code == 200


class TestEliminarDesafioRouter:
    def test_elimina_exitosamente(self):
        with patch("app.routers.desafios.desafios_service.eliminar_desafio", return_value={"mensaje": "ok"}):
            r = client.delete("/desafios/d1", headers=_HEADERS)
            assert r.status_code == 200

    def test_error_500(self):
        with patch("app.routers.desafios.desafios_service.eliminar_desafio", side_effect=HTTPException(500, "fallo")):
            r = client.delete("/desafios/d1", headers=_HEADERS)
            assert r.status_code == 500
