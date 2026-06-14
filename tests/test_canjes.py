"""Pruebas unitarias de canjes_service.

Los repositorios se reemplazan con mocks: ninguna prueba toca la red
ni la base de datos real.
"""
from unittest.mock import patch

from app.services import canjes_service


# ---------- pendientes ----------

class TestObtenerPendientes:
    @patch("app.services.canjes_service.canjes_repo")
    def test_devuelve_los_canjes_pendientes_del_padre(self, repo):
        repo.obtener_canjes_pendientes.return_value = [{"id": "canje-1"}]

        resultado = canjes_service.obtener_pendientes("padre-1")

        repo.obtener_canjes_pendientes.assert_called_once_with("padre-1")
        assert resultado == [{"id": "canje-1"}]

    @patch("app.services.canjes_service.canjes_repo")
    def test_hijo_con_canje_pendiente_devuelve_true(self, repo):
        repo.tiene_pendiente.return_value = True

        resultado = canjes_service.tiene_pendiente_hijo("hijo-1")

        assert resultado == {"tiene_pendiente": True}

    @patch("app.services.canjes_service.canjes_repo")
    def test_hijo_sin_canje_pendiente_devuelve_false(self, repo):
        repo.tiene_pendiente.return_value = False

        resultado = canjes_service.tiene_pendiente_hijo("hijo-1")

        assert resultado == {"tiene_pendiente": False}


# ---------- aprobar canje ----------

class TestAprobarCanje:
    @patch("app.services.canjes_service.recompensas_repo")
    @patch("app.services.canjes_service.canjes_repo")
    def test_aprobar_marca_estado_y_deshabilita_recompensas_del_hijo(self, repo, recompensas):
        repo.obtener_pendiente_de_hijo_por_id.return_value = {
            "id": "canje-1", "hijo_id": "hijo-1"
        }

        canjes_service.aprobar_canje("canje-1")

        repo.actualizar_estado_canje.assert_called_once_with("canje-1", "aprobado")
        recompensas.deshabilitar_todas.assert_called_once_with("hijo-1")

    @patch("app.services.canjes_service.recompensas_repo")
    @patch("app.services.canjes_service.canjes_repo")
    def test_aprobar_canje_inexistente_no_deshabilita_recompensas(self, repo, recompensas):
        repo.obtener_pendiente_de_hijo_por_id.return_value = None

        canjes_service.aprobar_canje("canje-fantasma")

        repo.actualizar_estado_canje.assert_called_once_with("canje-fantasma", "aprobado")
        recompensas.deshabilitar_todas.assert_not_called()


# ---------- rechazar canje ----------

class TestRechazarCanje:
    @patch("app.services.canjes_service.canjes_repo")
    def test_rechazar_marca_el_estado_como_rechazado(self, repo):
        canjes_service.rechazar_canje("canje-1")

        repo.actualizar_estado_canje.assert_called_once_with("canje-1", "rechazado")
