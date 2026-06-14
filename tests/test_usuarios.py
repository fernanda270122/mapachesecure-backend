"""Pruebas unitarias de usuarios_service.

El repositorio de usuarios se reemplaza con mocks: ninguna prueba toca
la red ni la base de datos real.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services import usuarios_service


# ---------- obtener usuarios ----------

class TestObtenerUsuarios:
    @patch("app.services.usuarios_service.usuarios_repo")
    def test_devuelve_todos_los_usuarios(self, repo):
        repo.get_all.return_value = [{"id": "u1"}, {"id": "u2"}]

        resultado = usuarios_service.obtener_usuarios()

        assert resultado == [{"id": "u1"}, {"id": "u2"}]

    @patch("app.services.usuarios_service.usuarios_repo")
    def test_con_error_devuelve_500(self, repo):
        repo.get_all.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            usuarios_service.obtener_usuarios()

        assert exc.value.status_code == 500


# ---------- obtener un usuario ----------

class TestObtenerUsuario:
    @patch("app.services.usuarios_service.usuarios_repo")
    def test_devuelve_el_primer_resultado(self, repo):
        repo.get_by_id.return_value = [{"id": "u1", "nombre": "Benja"}]

        resultado = usuarios_service.obtener_usuario("u1")

        assert resultado == {"id": "u1", "nombre": "Benja"}

    @patch("app.services.usuarios_service.usuarios_repo")
    def test_usuario_inexistente_devuelve_404(self, repo):
        repo.get_by_id.return_value = []

        with pytest.raises(HTTPException) as exc:
            usuarios_service.obtener_usuario("fantasma")

        assert exc.value.status_code == 404

    @patch("app.services.usuarios_service.usuarios_repo")
    def test_con_error_devuelve_500(self, repo):
        repo.get_by_id.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            usuarios_service.obtener_usuario("u1")

        assert exc.value.status_code == 500


# ---------- crear usuario ----------

class TestCrearUsuario:
    @patch("app.services.usuarios_service.usuarios_repo")
    def test_crear_filtra_los_campos_nulos(self, repo):
        usuario = MagicMock()
        usuario.model_dump.return_value = {
            "nombre": "Benja", "email": "benja@test.com",
            "edad": None, "padre_id": None,
        }

        usuarios_service.crear_usuario(usuario)

        datos_guardados = repo.create.call_args[0][0]
        assert datos_guardados == {"nombre": "Benja", "email": "benja@test.com"}
        assert "edad" not in datos_guardados
        assert "padre_id" not in datos_guardados

    @patch("app.services.usuarios_service.usuarios_repo")
    def test_crear_con_error_devuelve_500(self, repo):
        usuario = MagicMock()
        usuario.model_dump.return_value = {"nombre": "Benja"}
        repo.create.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            usuarios_service.crear_usuario(usuario)

        assert exc.value.status_code == 500


# ---------- hijos del padre ----------

class TestObtenerHijos:
    @patch("app.services.usuarios_service.usuarios_repo")
    def test_devuelve_los_hijos_del_padre(self, repo):
        repo.get_hijos.return_value = [{"id": "hijo-1"}]

        resultado = usuarios_service.obtener_hijos("padre-1")

        repo.get_hijos.assert_called_once_with("padre-1")
        assert resultado == [{"id": "hijo-1"}]


# ---------- configurar hijo ----------

class TestConfigurarHijo:
    @patch("app.services.usuarios_service.usuarios_repo")
    def test_configurar_actualiza_el_tiempo_limite(self, repo):
        config = SimpleNamespace(tiempo_limite_minutos=120)

        resultado = usuarios_service.configurar_hijo("hijo-1", config)

        assert resultado["mensaje"] == "Configuración actualizada"
        repo.update.assert_called_once_with("hijo-1", {"tiempo_limite_minutos": 120})

    @patch("app.services.usuarios_service.usuarios_repo")
    def test_configurar_con_error_devuelve_500(self, repo):
        config = SimpleNamespace(tiempo_limite_minutos=120)
        repo.update.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            usuarios_service.configurar_hijo("hijo-1", config)

        assert exc.value.status_code == 500


# ---------- avatar ----------

class TestActualizarAvatar:
    @patch("app.services.usuarios_service.usuarios_repo")
    def test_avatar_valido_se_actualiza(self, repo):
        resultado = usuarios_service.actualizar_tipo_avatar("u1", "ninja")

        assert resultado["tipo_avatar"] == "ninja"
        repo.update.assert_called_once_with("u1", {"tipo_avatar": "ninja"})

    @patch("app.services.usuarios_service.usuarios_repo")
    def test_avatar_invalido_devuelve_400(self, repo):
        with pytest.raises(HTTPException) as exc:
            usuarios_service.actualizar_tipo_avatar("u1", "robot")

        assert exc.value.status_code == 400
        repo.update.assert_not_called()

    @patch("app.services.usuarios_service.usuarios_repo")
    def test_todos_los_avatares_validos_se_aceptan(self, repo):
        for avatar in ("mago", "dormilon", "gamer", "ninja", "samuray", "princes"):
            resultado = usuarios_service.actualizar_tipo_avatar("u1", avatar)
            assert resultado["tipo_avatar"] == avatar


# ---------- foto de perfil ----------

class TestActualizarFotoPerfil:
    @patch("app.services.usuarios_service.usuarios_repo")
    def test_actualiza_la_foto_de_perfil(self, repo):
        resultado = usuarios_service.actualizar_foto_perfil("u1", "perfil3.jpeg")

        assert resultado["foto_perfil"] == "perfil3.jpeg"
        repo.update.assert_called_once_with("u1", {"foto_perfil": "perfil3.jpeg"})

    @patch("app.services.usuarios_service.usuarios_repo")
    def test_con_error_devuelve_500(self, repo):
        repo.update.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            usuarios_service.actualizar_foto_perfil("u1", "perfil3.jpeg")

        assert exc.value.status_code == 500
