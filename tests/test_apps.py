"""Pruebas unitarias de apps_service.

Los repositorios se reemplazan con mocks: ninguna prueba toca la red
ni la base de datos real.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services import apps_service


# ---------- apps bloqueadas ----------

class TestObtenerAppsBloqueadas:
    @patch("app.services.apps_service.apps_repo")
    def test_devuelve_las_apps_del_hijo(self, repo):
        repo.get_by_hijo.return_value = [{"id": "app-1", "package_name": "com.juego"}]

        resultado = apps_service.obtener_apps_bloqueadas("hijo-1")

        repo.get_by_hijo.assert_called_once_with("hijo-1")
        assert resultado == [{"id": "app-1", "package_name": "com.juego"}]

    @patch("app.services.apps_service.apps_repo")
    def test_con_error_devuelve_500(self, repo):
        repo.get_by_hijo.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            apps_service.obtener_apps_bloqueadas("hijo-1")

        assert exc.value.status_code == 500


class TestAgregarAppBloqueada:
    @patch("app.services.apps_service.apps_repo")
    def test_agrega_la_app_exitosamente(self, repo):
        app = MagicMock()
        app.model_dump.return_value = {"hijo_id": "hijo-1", "package_name": "com.juego"}
        repo.create.return_value = {"id": "app-1"}

        resultado = apps_service.agregar_app_bloqueada(app)

        assert "agregada exitosamente" in resultado["mensaje"]
        repo.create.assert_called_once_with({"hijo_id": "hijo-1", "package_name": "com.juego"})

    @patch("app.services.apps_service.apps_repo")
    def test_con_error_devuelve_500(self, repo):
        app = MagicMock()
        app.model_dump.return_value = {}
        repo.create.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            apps_service.agregar_app_bloqueada(app)

        assert exc.value.status_code == 500


class TestEliminarAppBloqueada:
    @patch("app.services.apps_service.apps_repo")
    def test_desbloquea_la_app(self, repo):
        resultado = apps_service.eliminar_app_bloqueada("app-1")

        assert resultado == {"mensaje": "App desbloqueada exitosamente"}
        repo.delete.assert_called_once_with("app-1")

    @patch("app.services.apps_service.apps_repo")
    def test_con_error_devuelve_500(self, repo):
        repo.delete.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            apps_service.eliminar_app_bloqueada("app-1")

        assert exc.value.status_code == 500


class TestActualizarAppBloqueada:
    @patch("app.services.apps_service.apps_repo")
    def test_actualiza_exitosamente(self, repo):
        repo.update.return_value = {"id": "app-1"}

        resultado = apps_service.actualizar_app_bloqueada("app-1", {"requiere_desafio": True})

        assert "actualizada exitosamente" in resultado["mensaje"]
        repo.update.assert_called_once_with("app-1", {"requiere_desafio": True})


# ---------- verificar app ----------

class TestVerificarApp:
    @patch("app.services.apps_service.apps_repo")
    def test_app_bloqueada_informa_si_requiere_desafio(self, repo):
        repo.get_by_hijo_y_package.return_value = [
            {"id": "app-1", "requiere_desafio": True}
        ]

        resultado = apps_service.verificar_app("hijo-1", "com.juego")

        assert resultado["bloqueada"] is True
        assert resultado["requiere_desafio"] is True

    @patch("app.services.apps_service.apps_repo")
    def test_app_no_bloqueada_devuelve_false(self, repo):
        repo.get_by_hijo_y_package.return_value = []

        resultado = apps_service.verificar_app("hijo-1", "com.calculadora")

        assert resultado == {"bloqueada": False}


# ---------- reportar uso ----------

class TestReportarUso:
    @patch("app.services.apps_service.apps_repo")
    def test_primer_uso_del_dia_crea_el_registro(self, repo):
        repo.get_uso_hoy.return_value = []

        resultado = apps_service.reportar_uso("hijo-1", 30)

        assert resultado["minutos_usados"] == 30
        repo.crear_uso.assert_called_once()
        repo.actualizar_uso.assert_not_called()

    @patch("app.services.apps_service.apps_repo")
    def test_uso_existente_actualiza_el_registro(self, repo):
        repo.get_uso_hoy.return_value = [{"id": "uso-1", "minutos_usados": 20}]

        apps_service.reportar_uso("hijo-1", 15)

        repo.actualizar_uso.assert_called_once_with("uso-1", 15)
        repo.crear_uso.assert_not_called()


# ---------- estado de tiempo de pantalla ----------

class TestObtenerEstado:
    @patch("app.repositories.usuarios_repo.get_by_id")
    @patch("app.services.apps_service.apps_repo")
    def test_dentro_del_limite_no_esta_bloqueado(self, apps_repo, get_by_id):
        apps_repo.get_uso_hoy.return_value = [{"minutos_usados": 40}]
        get_by_id.return_value = [{"tiempo_limite_minutos": 120}]

        resultado = apps_service.obtener_estado("hijo-1")

        assert resultado["bloqueado"] is False
        assert resultado["minutos_restantes"] == 80

    @patch("app.repositories.usuarios_repo.get_by_id")
    @patch("app.services.apps_service.apps_repo")
    def test_alcanzado_el_limite_queda_bloqueado(self, apps_repo, get_by_id):
        apps_repo.get_uso_hoy.return_value = [{"minutos_usados": 120}]
        get_by_id.return_value = [{"tiempo_limite_minutos": 120}]

        resultado = apps_service.obtener_estado("hijo-1")

        assert resultado["bloqueado"] is True
        assert resultado["minutos_restantes"] == 0

    @patch("app.repositories.usuarios_repo.get_by_id")
    @patch("app.services.apps_service.apps_repo")
    def test_sin_uso_registrado_cuenta_como_cero(self, apps_repo, get_by_id):
        apps_repo.get_uso_hoy.return_value = []
        get_by_id.return_value = [{"tiempo_limite_minutos": 120}]

        resultado = apps_service.obtener_estado("hijo-1")

        assert resultado["minutos_usados"] == 0
        assert resultado["minutos_restantes"] == 120

    @patch("app.repositories.usuarios_repo.get_by_id")
    @patch("app.services.apps_service.apps_repo")
    def test_sin_limite_configurado_usa_120_por_defecto(self, apps_repo, get_by_id):
        apps_repo.get_uso_hoy.return_value = [{"minutos_usados": 10}]
        get_by_id.return_value = [{"tiempo_limite_minutos": None}]

        resultado = apps_service.obtener_estado("hijo-1")

        assert resultado["tiempo_limite_minutos"] == 120

    @patch("app.repositories.usuarios_repo.get_by_id")
    @patch("app.services.apps_service.apps_repo")
    def test_hijo_inexistente_devuelve_404(self, apps_repo, get_by_id):
        apps_repo.get_uso_hoy.return_value = []
        get_by_id.return_value = []

        with pytest.raises(HTTPException) as exc:
            apps_service.obtener_estado("fantasma")

        assert exc.value.status_code == 404
