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
_RECOMPENSA = {"id": "r1", "titulo": "Premio", "costo_puntos": 50}


class TestObtenerCatalogoRouter:
    def test_devuelve_catalogo(self):
        with patch("app.routers.recompensas.recompensas_service.obtener_catalogo", return_value=[]):
            r = client.get("/recompensas/catalogo", headers=_HEADERS)
            assert r.status_code == 200


class TestCrearEnCatalogoRouter:
    def test_crea_en_catalogo(self):
        with patch("app.routers.recompensas.recompensas_service.agregar_al_catalogo", return_value={"id": "c1"}):
            r = client.post("/recompensas/catalogo", headers=_HEADERS, json={
                "nombre": "Helado", "puntos_sugeridos": 20, "icono": "🍦"
            })
            assert r.status_code == 200


class TestEliminarDelCatalogoRouter:
    def test_elimina_del_catalogo(self):
        with patch("app.routers.recompensas.recompensas_service.eliminar_del_catalogo", return_value={"ok": True}):
            r = client.delete("/recompensas/catalogo/c1", headers=_HEADERS)
            assert r.status_code == 200

    def test_no_autorizado(self):
        with patch("app.routers.recompensas.recompensas_service.eliminar_del_catalogo", side_effect=HTTPException(403, "no autorizado")):
            r = client.delete("/recompensas/catalogo/c1", headers=_HEADERS)
            assert r.status_code == 403


class TestHistorialCanjesRouter:
    def test_devuelve_historial(self):
        with patch("app.routers.recompensas.recompensas_service.historial_canjes", return_value=[]):
            r = client.get("/recompensas/historial/h1", headers=_HEADERS)
            assert r.status_code == 200


class TestCanjearRecompensaRouter:
    def test_canjea_exitosamente(self):
        with patch("app.routers.recompensas.recompensas_service.canjear_recompensa", return_value={"mensaje": "ok"}):
            r = client.post("/recompensas/canjear", headers=_HEADERS, json={"hijo_id": "h1", "recompensa_id": "r1"})
            assert r.status_code == 200

    def test_sin_puntos(self):
        with patch("app.routers.recompensas.recompensas_service.canjear_recompensa", side_effect=HTTPException(400, "sin puntos")):
            r = client.post("/recompensas/canjear", headers=_HEADERS, json={"hijo_id": "h1", "recompensa_id": "r1"})
            assert r.status_code == 400


class TestObtenerRecompensasRouter:
    def test_devuelve_recompensas(self):
        with patch("app.routers.recompensas.recompensas_service.obtener_recompensas", return_value=[_RECOMPENSA]):
            r = client.get("/recompensas/h1", headers=_HEADERS)
            assert r.status_code == 200


class TestCrearRecompensaRouter:
    def test_crea_recompensa(self):
        with patch("app.routers.recompensas.recompensas_service.crear_recompensa", return_value=_RECOMPENSA):
            r = client.post("/recompensas/", headers=_HEADERS, json={
                "padre_id": "p1", "hijo_id": "h1", "titulo": "Premio", "costo_puntos": 50
            })
            assert r.status_code == 200


class TestActualizarRecompensaRouter:
    def test_actualiza_exitosamente(self):
        with patch("app.routers.recompensas.recompensas_service.actualizar_recompensa", return_value=_RECOMPENSA):
            r = client.put("/recompensas/r1", headers=_HEADERS, json={"titulo": "Nuevo premio"})
            assert r.status_code == 200

    def test_error_500(self):
        with patch("app.routers.recompensas.recompensas_service.actualizar_recompensa", side_effect=HTTPException(500, "fallo")):
            r = client.put("/recompensas/r1", headers=_HEADERS, json={"titulo": "X"})
            assert r.status_code == 500
