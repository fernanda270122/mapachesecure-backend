"""Pruebas unitarias de auth_service.

Los repositorios y servicios externos (Supabase, Resend) se reemplazan con mocks:
ninguna prueba toca la red ni la base de datos real.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services import auth_service


def _respuesta_auth(usuario_id="usuario-123", con_sesion=False):
    """Simula la respuesta de Supabase Auth (sign_up / sign_in)."""
    respuesta = MagicMock()
    respuesta.user.id = usuario_id
    if con_sesion:
        respuesta.session.access_token = "token-acceso"
        respuesta.session.refresh_token = "token-refresh"
    return respuesta


def _datos_registro():
    return SimpleNamespace(
        email="padre@test.com", password="secreta123", nombre="Padre Test", rol="padre"
    )


def _datos_hijo():
    return SimpleNamespace(
        email="hijo@test.com", password="secreta123", nombre="Hijo Test",
        edad=10, sexo="M", nivel_escolar="primaria",
        personalidad="curioso", intereses=["videojuegos"],
    )


# ---------- registro ----------

class TestRegistro:
    @patch("app.services.auth_service.auth_repo")
    def test_registro_exitoso_crea_perfil_y_devuelve_datos(self, repo):
        repo.sign_up.return_value = _respuesta_auth()

        resultado = auth_service.registro(_datos_registro())

        assert resultado["mensaje"] == "Usuario registrado exitosamente"
        assert resultado["user_id"] == "usuario-123"
        assert resultado["rol"] == "padre"
        repo.create_perfil.assert_called_once_with({
            "id": "usuario-123", "email": "padre@test.com",
            "nombre": "Padre Test", "rol": "padre",
        })

    @patch("app.services.auth_service.auth_repo")
    def test_registro_sin_usuario_devuelve_400(self, repo):
        repo.sign_up.return_value = SimpleNamespace(user=None)

        with pytest.raises(HTTPException) as exc:
            auth_service.registro(_datos_registro())

        assert exc.value.status_code == 400
        repo.create_perfil.assert_not_called()

    @patch("app.services.auth_service.auth_repo")
    def test_registro_con_limite_de_correos_devuelve_429(self, repo):
        repo.sign_up.side_effect = Exception("email rate limit exceeded")

        with pytest.raises(HTTPException) as exc:
            auth_service.registro(_datos_registro())

        assert exc.value.status_code == 429
        assert "Límite de correos" in exc.value.detail

    @patch("app.services.auth_service.auth_repo")
    def test_registro_con_error_generico_devuelve_500(self, repo):
        repo.sign_up.side_effect = Exception("conexión perdida")

        with pytest.raises(HTTPException) as exc:
            auth_service.registro(_datos_registro())

        assert exc.value.status_code == 500
        assert "conexión perdida" in exc.value.detail


# ---------- Inicio de sesion ----------

class TestInicioDeSesion:
    @patch("app.services.auth_service.auth_repo")
    def test_inicio_sesion_exitoso_devuelve_tokens_y_perfil(self, repo):
        repo.sign_in.return_value = _respuesta_auth(con_sesion=True)
        repo.get_perfil.return_value = [{"rol": "padre", "nombre": "Padre Test"}]

        datos = SimpleNamespace(email="padre@test.com", password="secreta123")
        resultado = auth_service.login(datos)

        assert resultado["access_token"] == "token-acceso"
        assert resultado["refresh_token"] == "token-refresh"
        assert resultado["perfil"]["rol"] == "padre"

    @patch("app.services.auth_service.auth_repo")
    def test_inicio_sesion_sin_usuario_devuelve_401(self, repo):
        repo.sign_in.return_value = SimpleNamespace(user=None)

        datos = SimpleNamespace(email="padre@test.com", password="incorrecta")
        with pytest.raises(HTTPException) as exc:
            auth_service.login(datos)

        assert exc.value.status_code == 401

    @patch("app.services.auth_service.auth_repo")
    def test_inicio_sesion_sin_perfil_devuelve_perfil_nulo(self, repo):
        repo.sign_in.return_value = _respuesta_auth(con_sesion=True)
        repo.get_perfil.return_value = []

        datos = SimpleNamespace(email="padre@test.com", password="secreta123")
        resultado = auth_service.login(datos)

        assert resultado["perfil"] is None

    @patch("app.services.auth_service.auth_repo")
    def test_inicio_sesion_con_error_devuelve_500(self, repo):
        repo.sign_in.side_effect = Exception("Invalid login credentials")

        datos = SimpleNamespace(email="padre@test.com", password="secreta123")
        with pytest.raises(HTTPException) as exc:
            auth_service.login(datos)

        assert exc.value.status_code == 500


# ---------- refrescar token ----------

class TestRefrescarToken:
    @patch("app.database.supabase")
    def test_refrescar_token_exitoso_devuelve_tokens_nuevos(self, supabase):
        respuesta = MagicMock()
        respuesta.session.access_token = "nuevo-acceso"
        respuesta.session.refresh_token = "nuevo-refresh"
        supabase.auth.refresh_session.return_value = respuesta

        resultado = auth_service.refresh_token("refresh-viejo")

        assert resultado["access_token"] == "nuevo-acceso"
        assert resultado["refresh_token"] == "nuevo-refresh"

    @patch("app.database.supabase")
    def test_refrescar_token_sin_sesion_devuelve_401(self, supabase):
        supabase.auth.refresh_session.return_value = SimpleNamespace(session=None)

        with pytest.raises(HTTPException) as exc:
            auth_service.refresh_token("refresh-invalido")

        assert exc.value.status_code == 401

    @patch("app.database.supabase")
    def test_refrescar_token_con_error_devuelve_401(self, supabase):
        supabase.auth.refresh_session.side_effect = Exception("token expirado")

        with pytest.raises(HTTPException) as exc:
            auth_service.refresh_token("refresh-expirado")

        assert exc.value.status_code == 401


# ---------- Cerrar sesion ----------

class TestCerrarSesion:
    @patch("app.services.auth_service.auth_repo")
    def test_cerrar_sesion_exitoso(self, repo):
        resultado = auth_service.logout()

        assert resultado == {"mensaje": "Sesion cerrada exitosamente"}
        repo.sign_out.assert_called_once()

    @patch("app.services.auth_service.auth_repo")
    def test_cerrar_sesion_con_error_devuelve_500(self, repo):
        repo.sign_out.side_effect = Exception("sin sesión activa")

        with pytest.raises(HTTPException) as exc:
            auth_service.logout()

        assert exc.value.status_code == 500


# ---------- vincular hijo ----------

class TestVincularHijo:
    @patch("app.services.auth_service.auth_repo")
    def test_vincular_exitoso(self, repo):
        repo.vincular_hijo.return_value = [{"id": "hijo-1", "padre_id": "padre-1"}]

        resultado = auth_service.vincular_hijo("hijo-1", "padre-1")

        assert resultado["mensaje"] == "Hijo vinculado al padre exitosamente"
        assert resultado["data"]["padre_id"] == "padre-1"

    @patch("app.services.auth_service.auth_repo")
    def test_vincular_hijo_inexistente_devuelve_404(self, repo):
        repo.vincular_hijo.return_value = []

        with pytest.raises(HTTPException) as exc:
            auth_service.vincular_hijo("hijo-fantasma", "padre-1")

        assert exc.value.status_code == 404


# ---------- registro de hijo ----------

class TestRegistroHijo:
    @patch("app.services.auth_service.auth_repo")
    def test_registro_hijo_crea_cuenta_con_padre_vinculado(self, repo):
        repo.admin_create_user.return_value = _respuesta_auth(usuario_id="hijo-9")

        resultado = auth_service.registro_hijo(_datos_hijo(), padre_id="padre-1")

        assert resultado["mensaje"] == "Hijo registrado exitosamente"
        assert resultado["user_id"] == "hijo-9"
        perfil = repo.create_perfil.call_args[0][0]
        assert perfil["padre_id"] == "padre-1"
        assert perfil["rol"] == "hijo"
        assert perfil["edad"] == 10

    @patch("app.services.auth_service.auth_repo")
    def test_registro_hijo_con_correo_duplicado_devuelve_400(self, repo):
        repo.admin_create_user.side_effect = Exception(
            "duplicate key value violates unique constraint (23505)"
        )

        with pytest.raises(HTTPException) as exc:
            auth_service.registro_hijo(_datos_hijo(), padre_id="padre-1")

        assert exc.value.status_code == 400
        assert "ya está registrado" in exc.value.detail

    @patch("app.services.auth_service.auth_repo")
    def test_registro_hijo_sin_usuario_devuelve_400(self, repo):
        repo.admin_create_user.return_value = SimpleNamespace(user=None)

        with pytest.raises(HTTPException) as exc:
            auth_service.registro_hijo(_datos_hijo(), padre_id="padre-1")

        assert exc.value.status_code == 400


# ---------- recuperar y cambiar contraseña ----------

class TestContrasena:
    @patch("app.services.auth_service.auth_repo")
    def test_recuperar_contrasena_exitoso(self, repo):
        resultado = auth_service.recuperar_password("padre@test.com")

        assert resultado == {"mensaje": "Correo de recuperación enviado"}
        repo.reset_password.assert_called_once_with("padre@test.com")

    @patch("app.services.auth_service.auth_repo")
    def test_recuperar_contrasena_con_error_devuelve_500(self, repo):
        repo.reset_password.side_effect = Exception("email rate limit exceeded")

        with pytest.raises(HTTPException) as exc:
            auth_service.recuperar_password("padre@test.com")

        assert exc.value.status_code == 500

    @patch("app.services.auth_service.auth_repo")
    def test_cambiar_contrasena_exitoso(self, repo):
        resultado = auth_service.cambiar_password("token-acceso", "nueva-secreta")

        assert resultado == {"mensaje": "Contraseña actualizada exitosamente"}
        repo.cambiar_password.assert_called_once_with("token-acceso", "nueva-secreta")

    @patch("app.services.auth_service.auth_repo")
    def test_cambiar_contrasena_con_error_devuelve_500(self, repo):
        repo.cambiar_password.side_effect = Exception("token inválido")

        with pytest.raises(HTTPException) as exc:
            auth_service.cambiar_password("token-malo", "nueva-secreta")

        assert exc.value.status_code == 500
