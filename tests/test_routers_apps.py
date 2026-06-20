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
_APP = {"id": "a1", "hijo_id": "h1", "package_name": "com.test", "nombre_app": "Test"}


class TestObtenerAppsBloqueadasRouter:
    def test_devuelve_lista(self):
        with patch("app.routers.apps.apps_service.obtener_apps_bloqueadas", return_value=[_APP]):
            r = client.get("/apps/h1", headers=_HEADERS)
            assert r.status_code == 200

    def test_error_500(self):
        with patch("app.routers.apps.apps_service.obtener_apps_bloqueadas", side_effect=HTTPException(500, "fallo")):
            r = client.get("/apps/h1", headers=_HEADERS)
            assert r.status_code == 500


class TestAgregarAppBloqueadaRouter:
    def test_agrega_exitosamente(self):
        with patch("app.routers.apps.apps_service.agregar_app_bloqueada", return_value=_APP):
            r = client.post("/apps/", headers=_HEADERS, json={
                "hijo_id": "h1", "package_name": "com.test",
                "nombre_app": "Test", "requiere_desafio": True
            })
            assert r.status_code == 200


class TestEliminarAppBloqueadaRouter:
    def test_elimina_exitosamente(self):
        with patch("app.routers.apps.apps_service.eliminar_app_bloqueada", return_value={"mensaje": "ok"}):
            r = client.delete("/apps/a1", headers=_HEADERS)
            assert r.status_code == 200


class TestActualizarAppBloqueadaRouter:
    def test_actualiza_exitosamente(self):
        with patch("app.routers.apps.apps_service.actualizar_app_bloqueada", return_value=_APP):
            r = client.put("/apps/a1", headers=_HEADERS, json={"requiere_desafio": False})
            assert r.status_code == 200


class TestVerificarAppRouter:
    def test_app_bloqueada(self):
        with patch("app.routers.apps.apps_service.verificar_app", return_value={"bloqueada": True}):
            r = client.get("/apps/verificar/h1/com.test", headers=_HEADERS)
            assert r.status_code == 200

    def test_app_no_bloqueada(self):
        with patch("app.routers.apps.apps_service.verificar_app", return_value={"bloqueada": False}):
            r = client.get("/apps/verificar/h1/com.libre", headers=_HEADERS)
            assert r.status_code == 200


class TestReporteUsoRouter:
    def test_reporta_exitosamente(self):
        with patch("app.routers.apps.apps_service.reportar_uso", return_value={"mensaje": "ok"}):
            r = client.post("/apps/reporte-uso", headers=_HEADERS, json={"hijo_id": "h1", "minutos": 30})
            assert r.status_code == 200


class TestObtenerEstadoRouter:
    def test_devuelve_estado(self):
        with patch("app.routers.apps.apps_service.obtener_estado", return_value={"bloqueado": False}):
            r = client.get("/apps/estado/h1", headers=_HEADERS)
            assert r.status_code == 200

    def test_hijo_no_encontrado(self):
        with patch("app.routers.apps.apps_service.obtener_estado", side_effect=HTTPException(404, "no existe")):
            r = client.get("/apps/estado/fantasma", headers=_HEADERS)
            assert r.status_code == 404
