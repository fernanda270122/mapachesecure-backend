from unittest.mock import MagicMock, patch
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


class TestAuthRegistroRouter:
    def test_registro_exitoso(self):
        with patch("app.routers.auth.auth_service.registro", return_value={"user_id": "1", "rol": "padre"}):
            r = client.post("/auth/registro", json={
                "email": "p@test.com", "password": "123456", "nombre": "Padre", "rol": "padre"
            })
            assert r.status_code == 200

    def test_registro_error_devuelve_detalle(self):
        from fastapi import HTTPException
        with patch("app.routers.auth.auth_service.registro", side_effect=HTTPException(400, "error")):
            r = client.post("/auth/registro", json={
                "email": "p@test.com", "password": "123456", "nombre": "Padre", "rol": "padre"
            })
            assert r.status_code == 400


class TestAuthLoginRouter:
    def test_login_exitoso(self):
        with patch("app.routers.auth.auth_service.login", return_value={"access_token": "tok"}):
            r = client.post("/auth/login", json={"email": "p@test.com", "password": "123456"})
            assert r.status_code == 200

    def test_login_error_401(self):
        from fastapi import HTTPException
        with patch("app.routers.auth.auth_service.login", side_effect=HTTPException(401, "no auth")):
            r = client.post("/auth/login", json={"email": "p@test.com", "password": "mal"})
            assert r.status_code == 401


class TestAuthLogoutRouter:
    def test_logout_exitoso(self):
        with patch("app.routers.auth.auth_service.logout", return_value={"mensaje": "ok"}):
            r = client.post("/auth/logout", headers=_HEADERS)
            assert r.status_code == 200


class TestAuthVincularHijoRouter:
    def test_vincular_exitoso(self):
        with patch("app.routers.auth.auth_service.vincular_hijo", return_value={"mensaje": "ok"}):
            r = client.put("/auth/vincular-hijo?hijo_id=h1&padre_id=p1", headers=_HEADERS)
            assert r.status_code == 200

    def test_vincular_hijo_no_encontrado(self):
        from fastapi import HTTPException
        with patch("app.routers.auth.auth_service.vincular_hijo", side_effect=HTTPException(404, "no existe")):
            r = client.put("/auth/vincular-hijo?hijo_id=x&padre_id=p1", headers=_HEADERS)
            assert r.status_code == 404


class TestAuthRegistroHijoRouter:
    def test_registro_hijo_exitoso(self):
        with patch("app.routers.auth.auth_service.registro_hijo", return_value={"user_id": "h1"}):
            r = client.post("/auth/registro-hijo", headers=_HEADERS, json={
                "nombre": "Hijo", "email": "h@test.com", "password": "123456"
            })
            assert r.status_code == 200


class TestAuthRefreshRouter:
    def test_refresh_exitoso(self):
        with patch("app.routers.auth.auth_service.refresh_token", return_value={"access_token": "nuevo"}):
            r = client.post("/auth/refresh", json={"refresh_token": "viejo"})
            assert r.status_code == 200


class TestAuthPasswordRouter:
    def test_recuperar_password_exitoso(self):
        with patch("app.routers.auth.auth_service.recuperar_password", return_value={"mensaje": "ok"}):
            r = client.post("/auth/recuperar-password", json={"email": "p@test.com"})
            assert r.status_code == 200

    def test_cambiar_password_exitoso(self):
        with patch("app.routers.auth.auth_service.cambiar_password", return_value={"mensaje": "ok"}):
            r = client.post("/auth/cambiar-password", json={"access_token": "tok", "nueva_password": "nueva"})
            assert r.status_code == 200
