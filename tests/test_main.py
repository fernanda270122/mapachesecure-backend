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


class TestRoot:
    def test_root_devuelve_200(self):
        r = client.get("/")
        assert r.status_code == 200

    def test_root_contiene_version(self):
        r = client.get("/")
        assert "version" in r.json()

    def test_root_contiene_mensaje(self):
        r = client.get("/")
        assert "mensaje" in r.json()


class TestDependencies:
    def test_token_valido_devuelve_usuario(self):
        mock_resp = MagicMock()
        mock_resp.user = MagicMock()
        mock_resp.user.id = "uid-123"

        with patch("app.dependencies.supabase") as mock_sb:
            mock_sb.auth.get_user.return_value = mock_resp
            from app.dependencies import get_current_user as gcu
            from fastapi.security import HTTPAuthorizationCredentials
            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token-valido")
            resultado = gcu(creds)
            assert resultado.id == "uid-123"

    def test_token_sin_usuario_devuelve_401(self):
        mock_resp = MagicMock()
        mock_resp.user = None

        with patch("app.dependencies.supabase") as mock_sb:
            mock_sb.auth.get_user.return_value = mock_resp
            from app.dependencies import get_current_user as gcu
            from fastapi import HTTPException
            from fastapi.security import HTTPAuthorizationCredentials
            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token-malo")
            try:
                gcu(creds)
                assert False, "Debería lanzar HTTPException"
            except HTTPException as e:
                assert e.status_code == 401

    def test_excepcion_en_supabase_devuelve_401(self):
        with patch("app.dependencies.supabase") as mock_sb:
            mock_sb.auth.get_user.side_effect = Exception("fallo de red")
            from app.dependencies import get_current_user as gcu
            from fastapi import HTTPException
            from fastapi.security import HTTPAuthorizationCredentials
            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token-roto")
            try:
                gcu(creds)
                assert False, "Debería lanzar HTTPException"
            except HTTPException as e:
                assert e.status_code == 401
