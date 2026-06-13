"""Pruebas unitarias de recompensas_service.

Los repositorios se reemplazan con mocks: ninguna prueba toca la red
ni la base de datos real.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services import recompensas_service


def _recompensa_nueva(hijo_id="hijo-1", titulo="Helado"):
    """Simula el modelo Pydantic que llega desde el router."""
    recompensa = MagicMock()
    recompensa.hijo_id = hijo_id
    recompensa.titulo = titulo
    recompensa.model_dump.return_value = {
        "hijo_id": hijo_id, "titulo": titulo, "costo_puntos": 100
    }
    return recompensa


def _datos_canje(recompensa_id="recompensa-1", hijo_id="hijo-1"):
    return SimpleNamespace(recompensa_id=recompensa_id, hijo_id=hijo_id)


# ---------- obtener recompensas ----------

class TestObtenerRecompensas:
    @patch("app.services.recompensas_service.recompensas_repo")
    def test_elimina_recompensas_con_titulo_duplicado(self, repo):
        repo.get_by_hijo.return_value = [
            {"id": "r1", "titulo": "Helado"},
            {"id": "r2", "titulo": "Helado"},
            {"id": "r3", "titulo": "Cine"},
        ]

        resultado = recompensas_service.obtener_recompensas("hijo-1")

        assert len(resultado) == 2
        assert [r["titulo"] for r in resultado] == ["Helado", "Cine"]

    @patch("app.services.recompensas_service.recompensas_repo")
    def test_con_error_devuelve_500(self, repo):
        repo.get_by_hijo.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            recompensas_service.obtener_recompensas("hijo-1")

        assert exc.value.status_code == 500


# ---------- crear recompensa ----------

class TestCrearRecompensa:
    @patch("app.services.recompensas_service.recompensas_repo")
    def test_crea_una_recompensa_nueva(self, repo):
        repo.get_by_hijo_y_titulo.return_value = []
        repo.create.return_value = {"id": "r-nueva"}

        resultado = recompensas_service.crear_recompensa(_recompensa_nueva())

        assert "creada exitosamente" in resultado["mensaje"]
        repo.create.assert_called_once_with({
            "hijo_id": "hijo-1", "titulo": "Helado", "costo_puntos": 100
        })

    @patch("app.services.recompensas_service.recompensas_repo")
    def test_reactiva_una_recompensa_que_estaba_desactivada(self, repo):
        repo.get_by_hijo_y_titulo.return_value = [
            {"id": "r1", "titulo": "Helado", "disponible": False}
        ]

        resultado = recompensas_service.crear_recompensa(_recompensa_nueva())

        assert resultado["mensaje"] == "Recompensa reactivada"
        repo.update.assert_called_once_with("r1", {"disponible": True})
        repo.create.assert_not_called()

    @patch("app.services.recompensas_service.recompensas_repo")
    def test_no_duplica_una_recompensa_que_ya_esta_disponible(self, repo):
        repo.get_by_hijo_y_titulo.return_value = [
            {"id": "r1", "titulo": "Helado", "disponible": True}
        ]

        resultado = recompensas_service.crear_recompensa(_recompensa_nueva())

        assert resultado["mensaje"] == "Recompensa reactivada"
        repo.update.assert_not_called()
        repo.create.assert_not_called()


# ---------- canjear recompensa ----------

class TestCanjearRecompensa:
    @patch("app.services.recompensas_service.recompensas_repo")
    def test_recompensa_inexistente_devuelve_404(self, repo):
        repo.get_by_id.return_value = []

        with pytest.raises(HTTPException) as exc:
            recompensas_service.canjear_recompensa(_datos_canje())

        assert exc.value.status_code == 404

    @patch("app.services.recompensas_service.desafios_repo")
    @patch("app.services.recompensas_service.recompensas_repo")
    def test_sin_puntos_suficientes_no_registra_el_canje(self, repo, desafios):
        repo.get_by_id.return_value = [{"id": "recompensa-1", "costo_puntos": 200}]
        desafios.get_puntos.return_value = [{"total_puntos": 50}]

        resultado = recompensas_service.canjear_recompensa(_datos_canje())

        assert "No tienes suficientes puntos" in resultado["mensaje"]
        assert resultado["puntos_actuales"] == 50
        assert resultado["puntos_necesarios"] == 200
        repo.registrar_canje.assert_not_called()

    @patch("app.services.recompensas_service.desafios_repo")
    @patch("app.services.recompensas_service.recompensas_repo")
    def test_hijo_sin_historial_de_puntos_cuenta_como_cero(self, repo, desafios):
        repo.get_by_id.return_value = [{"id": "recompensa-1", "costo_puntos": 10}]
        desafios.get_puntos.return_value = []

        resultado = recompensas_service.canjear_recompensa(_datos_canje())

        assert resultado["puntos_actuales"] == 0
        repo.registrar_canje.assert_not_called()

    @patch("app.services.recompensas_service.desafios_repo")
    @patch("app.services.recompensas_service.recompensas_repo")
    def test_con_puntos_suficientes_registra_canje_pendiente(self, repo, desafios):
        repo.get_by_id.return_value = [{"id": "recompensa-1", "costo_puntos": 100}]
        desafios.get_puntos.return_value = [{"total_puntos": 150}]

        resultado = recompensas_service.canjear_recompensa(_datos_canje())

        assert resultado["pendiente"] is True
        repo.registrar_canje.assert_called_once_with({
            "hijo_id": "hijo-1", "recompensa_id": "recompensa-1", "estado": "pendiente"
        })

    @patch("app.services.recompensas_service.recompensas_repo")
    def test_con_error_devuelve_500(self, repo):
        repo.get_by_id.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            recompensas_service.canjear_recompensa(_datos_canje())

        assert exc.value.status_code == 500


# ---------- historial de canjes ----------

class TestHistorialCanjes:
    @patch("app.services.recompensas_service.recompensas_repo")
    def test_devuelve_el_historial_del_hijo(self, repo):
        repo.get_historial_canjes.return_value = [{"id": "canje-1"}]

        resultado = recompensas_service.historial_canjes("hijo-1")

        repo.get_historial_canjes.assert_called_once_with("hijo-1")
        assert resultado == [{"id": "canje-1"}]


# ---------- catalogo de recompensas ----------

class TestCatalogo:
    @patch("app.services.recompensas_service.catalogo_repo")
    def test_obtener_catalogo_devuelve_la_lista(self, catalogo):
        catalogo.get_all.return_value = [{"id": "c1", "titulo": "Cine"}]

        resultado = recompensas_service.obtener_catalogo()

        assert resultado == [{"id": "c1", "titulo": "Cine"}]

    @patch("app.services.recompensas_service.catalogo_repo")
    def test_agregar_guarda_quien_la_creo(self, catalogo):
        datos = MagicMock()
        datos.model_dump.return_value = {"titulo": "Cine", "costo_puntos": 300}

        recompensas_service.agregar_al_catalogo(datos, padre_id="padre-1")

        nuevo = catalogo.create.call_args[0][0]
        assert nuevo["creado_por"] == "padre-1"
        assert nuevo["titulo"] == "Cine"

    @patch("app.services.recompensas_service.catalogo_repo")
    def test_eliminar_recompensa_ajena_devuelve_403(self, catalogo):
        catalogo.delete.return_value = None

        with pytest.raises(HTTPException) as exc:
            recompensas_service.eliminar_del_catalogo("c1", padre_id="padre-intruso")

        assert exc.value.status_code == 403

    @patch("app.services.recompensas_service.catalogo_repo")
    def test_eliminar_recompensa_propia_exitoso(self, catalogo):
        catalogo.delete.return_value = {"id": "c1"}

        resultado = recompensas_service.eliminar_del_catalogo("c1", padre_id="padre-1")

        assert resultado == {"mensaje": "Recompensa eliminada del catálogo"}
        catalogo.delete.assert_called_once_with("c1", "padre-1")


# ---------- actualizar recompensa ----------

class TestActualizarRecompensa:
    @patch("app.services.recompensas_service.recompensas_repo")
    def test_actualizar_exitoso(self, repo):
        repo.update.return_value = {"id": "r1", "costo_puntos": 80}

        resultado = recompensas_service.actualizar_recompensa("r1", {"costo_puntos": 80})

        assert resultado["mensaje"] == "Recompensa actualizada exitosamente"
        repo.update.assert_called_once_with("r1", {"costo_puntos": 80})

    @patch("app.services.recompensas_service.recompensas_repo")
    def test_actualizar_con_error_devuelve_500(self, repo):
        repo.update.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            recompensas_service.actualizar_recompensa("r1", {"costo_puntos": 80})

        assert exc.value.status_code == 500
