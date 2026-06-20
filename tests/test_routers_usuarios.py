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
_USUARIO = {"id": "u1", "nombre": "Test", "rol": "padre"}


class TestObtenerUsuariosRouter:
    def test_devuelve_lista(self):
        with patch("app.routers.usuarios.usuarios_service.obtener_usuarios", return_value=[_USUARIO]):
            r = client.get("/usuarios/", headers=_HEADERS)
            assert r.status_code == 200

    def test_error_500(self):
        with patch("app.routers.usuarios.usuarios_service.obtener_usuarios", side_effect=HTTPException(500, "fallo")):
            r = client.get("/usuarios/", headers=_HEADERS)
            assert r.status_code == 500


class TestObtenerUsuarioRouter:
    def test_devuelve_usuario(self):
        with patch("app.routers.usuarios.usuarios_service.obtener_usuario", return_value=_USUARIO):
            r = client.get("/usuarios/u1", headers=_HEADERS)
            assert r.status_code == 200

    def test_usuario_no_encontrado(self):
        with patch("app.routers.usuarios.usuarios_service.obtener_usuario", side_effect=HTTPException(404, "no existe")):
            r = client.get("/usuarios/fantasma", headers=_HEADERS)
            assert r.status_code == 404


class TestCrearUsuarioRouter:
    def test_crea_usuario(self):
        with patch("app.routers.usuarios.usuarios_service.crear_usuario", return_value=_USUARIO):
            r = client.post("/usuarios/", headers=_HEADERS, json={"nombre": "Test", "rol": "padre"})
            assert r.status_code == 200

    def test_error_al_crear(self):
        with patch("app.routers.usuarios.usuarios_service.crear_usuario", side_effect=HTTPException(500, "fallo")):
            r = client.post("/usuarios/", headers=_HEADERS, json={"nombre": "Test", "rol": "padre"})
            assert r.status_code == 500


class TestObtenerHijosRouter:
    def test_devuelve_hijos(self):
        with patch("app.routers.usuarios.usuarios_service.obtener_hijos", return_value=[]):
            r = client.get("/usuarios/p1/hijos", headers=_HEADERS)
            assert r.status_code == 200


class TestConfigurarHijoRouter:
    def test_configura_exitosamente(self):
        with patch("app.routers.usuarios.usuarios_service.configurar_hijo", return_value={"ok": True}):
            r = client.put("/usuarios/h1/configuracion", headers=_HEADERS, json={"tiempo_limite_minutos": 60})
            assert r.status_code == 200


class TestActualizarAvatarRouter:
    def test_avatar_actualizado(self):
        with patch("app.routers.usuarios.usuarios_service.actualizar_tipo_avatar", return_value={"ok": True}):
            r = client.put("/usuarios/u1/tipo-avatar", headers=_HEADERS, json={"tipo_avatar": "mapache"})
            assert r.status_code == 200


class TestActualizarFotoPerfilRouter:
    def test_foto_actualizada(self):
        with patch("app.routers.usuarios.usuarios_service.actualizar_foto_perfil", return_value={"ok": True}):
            r = client.put("/usuarios/u1/foto-perfil", headers=_HEADERS, json={"foto_perfil": "url"})
            assert r.status_code == 200


