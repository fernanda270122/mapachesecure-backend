"""Pruebas unitarias de desafios_service.

Los repositorios y el servicio de notificaciones se reemplazan con mocks:
ninguna prueba toca la red ni la base de datos real.
"""
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.services import desafios_service


def _datos_completar():
    return SimpleNamespace(
        desafio_id="desafio-1", hijo_id="hijo-1", foto_url="https://fotos/evidencia.jpg"
    )


def _desafio(puntos=50, titulo="Leer un libro"):
    return [{"id": "desafio-1", "titulo": titulo, "puntos": puntos}]


# ---------- obtener desafios ----------

class TestObtenerDesafios:
    @patch("app.services.desafios_service.desafios_repo")
    def test_devuelve_la_lista_del_repositorio(self, repo):
        repo.get_all.return_value = _desafio()

        resultado = desafios_service.obtener_desafios()

        assert resultado == _desafio()

    @patch("app.services.desafios_service.desafios_repo")
    def test_con_error_devuelve_500(self, repo):
        repo.get_all.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            desafios_service.obtener_desafios()

        assert exc.value.status_code == 500

    @patch("app.services.desafios_service.desafios_repo")
    def test_por_tipo_consulta_el_tipo_pedido(self, repo):
        repo.get_by_tipo.return_value = _desafio(titulo="Desafío diario")

        resultado = desafios_service.obtener_por_tipo("diario")

        repo.get_by_tipo.assert_called_once_with("diario")
        assert resultado[0]["titulo"] == "Desafío diario"


# ---------- completar desafio ----------

class TestCompletarDesafio:
    @patch("app.services.desafios_service.notificaciones_service")
    @patch("app.services.desafios_service.desafios_repo")
    def test_completar_registra_evidencia_sin_validar_y_sin_puntos(self, repo, notificaciones):
        repo.get_by_id.return_value = _desafio()

        resultado = desafios_service.completar_desafio(_datos_completar())

        registro = repo.registrar_completado.call_args[0][0]
        assert registro["validado"] is False
        assert registro["puntos_otorgados"] == 0
        assert registro["foto_url"] == "https://fotos/evidencia.jpg"
        assert resultado["validado"] is False

    @patch("app.services.desafios_service.notificaciones_service")
    @patch("app.services.desafios_service.desafios_repo")
    def test_completar_desactiva_el_desafio_y_notifica_al_padre(self, repo, notificaciones):
        repo.get_by_id.return_value = _desafio(titulo="Ordenar la pieza")

        desafios_service.completar_desafio(_datos_completar())

        repo.actualizar_estado.assert_called_once_with("desafio-1", False)
        notificaciones.enviar_notificacion_evidencia.assert_called_once_with(
            "hijo-1", "Ordenar la pieza"
        )

    @patch("app.services.desafios_service.desafios_repo")
    def test_completar_desafio_inexistente_devuelve_404(self, repo):
        repo.get_by_id.return_value = []

        with pytest.raises(HTTPException) as exc:
            desafios_service.completar_desafio(_datos_completar())

        assert exc.value.status_code == 404
        repo.registrar_completado.assert_not_called()

    @patch("app.services.desafios_service.desafios_repo")
    def test_completar_con_error_devuelve_500(self, repo):
        repo.get_by_id.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            desafios_service.completar_desafio(_datos_completar())

        assert exc.value.status_code == 500


# ---------- puntos del hijo ----------

class TestObtenerPuntos:
    @patch("app.services.desafios_service.desafios_repo")
    def test_hijo_sin_puntos_devuelve_total_cero(self, repo):
        repo.get_puntos.return_value = []

        resultado = desafios_service.obtener_puntos("hijo-1")

        assert resultado == {"hijo_id": "hijo-1", "total_puntos": 0}

    @patch("app.services.desafios_service.desafios_repo")
    def test_hijo_con_puntos_devuelve_su_total(self, repo):
        repo.get_puntos.return_value = [{"hijo_id": "hijo-1", "total_puntos": 150}]

        resultado = desafios_service.obtener_puntos("hijo-1")

        assert resultado["total_puntos"] == 150


# ---------- validar desafio (decision del padre) ----------

class TestValidarDesafio:
    @patch("app.services.desafios_service.desafios_repo")
    def test_validar_registro_inexistente_devuelve_404(self, repo):
        repo.get_completado_by_id.return_value = []

        with pytest.raises(HTTPException) as exc:
            desafios_service.validar_desafio("completado-1", aprobado=True)

        assert exc.value.status_code == 404

    @patch("app.services.desafios_service.notificaciones_service")
    @patch("app.services.desafios_service.desafios_repo")
    def test_aprobar_otorga_los_puntos_del_desafio(self, repo, notificaciones):
        repo.get_completado_by_id.return_value = [
            {"id": "completado-1", "desafio_id": "desafio-1", "hijo_id": "hijo-1"}
        ]
        repo.get_by_id.return_value = _desafio(puntos=80)

        resultado = desafios_service.validar_desafio("completado-1", aprobado=True)

        assert resultado["puntos_otorgados"] == 80
        repo.actualizar_completado.assert_called_once_with(
            "completado-1", {"validado": True, "puntos_otorgados": 80}
        )
        notificaciones.enviar_notificacion_validacion.assert_called_once_with(
            "hijo-1", True, "Leer un libro"
        )

    @patch("app.services.desafios_service.notificaciones_service")
    @patch("app.services.desafios_service.desafios_repo")
    def test_aprobar_deja_el_desafio_desactivado(self, repo, notificaciones):
        repo.get_completado_by_id.return_value = [
            {"id": "completado-1", "desafio_id": "desafio-1", "hijo_id": "hijo-1"}
        ]
        repo.get_by_id.return_value = _desafio()

        desafios_service.validar_desafio("completado-1", aprobado=True)

        repo.actualizar_estado.assert_called_once_with("desafio-1", False)

    @patch("app.services.desafios_service.notificaciones_service")
    @patch("app.services.desafios_service.desafios_repo")
    def test_rechazar_elimina_la_evidencia_y_reactiva_el_desafio(self, repo, notificaciones):
        repo.get_completado_by_id.return_value = [
            {"id": "completado-1", "desafio_id": "desafio-1", "hijo_id": "hijo-1"}
        ]
        repo.get_by_id.return_value = _desafio()

        resultado = desafios_service.validar_desafio("completado-1", aprobado=False)

        assert resultado["puntos_otorgados"] == 0
        repo.delete_completado.assert_called_once_with("completado-1")
        repo.actualizar_estado.assert_called_once_with("desafio-1", True)
        notificaciones.enviar_notificacion_validacion.assert_called_once_with(
            "hijo-1", False, "Leer un libro"
        )

    @patch("app.services.desafios_service.notificaciones_service")
    @patch("app.services.desafios_service.desafios_repo")
    def test_rechazar_con_desafio_borrado_usa_titulo_generico(self, repo, notificaciones):
        repo.get_completado_by_id.return_value = [
            {"id": "completado-1", "desafio_id": "desafio-1", "hijo_id": "hijo-1"}
        ]
        repo.get_by_id.return_value = []

        desafios_service.validar_desafio("completado-1", aprobado=False)

        notificaciones.enviar_notificacion_validacion.assert_called_once_with(
            "hijo-1", False, "desafío"
        )


# ---------- pendientes por revisar ----------

class TestObtenerPendientes:
    @patch("app.services.desafios_service.usuarios_repo")
    def test_padre_sin_hijos_devuelve_lista_vacia(self, usuarios):
        usuarios.get_hijos.return_value = []

        resultado = desafios_service.obtener_pendientes("padre-1")

        assert resultado == []

    @patch("app.services.desafios_service.desafios_repo")
    @patch("app.services.desafios_service.usuarios_repo")
    def test_arma_los_pendientes_con_titulo_y_nombre_del_hijo(self, usuarios, repo):
        usuarios.get_hijos.return_value = [{"id": "hijo-1", "nombre": "Benja"}]
        repo.get_pendientes_hijo.return_value = [
            {"id": "completado-1", "desafio_id": "desafio-1", "foto_url": "https://foto.jpg"}
        ]
        repo.get_by_id.return_value = _desafio(titulo="Lavar la loza")

        resultado = desafios_service.obtener_pendientes("padre-1")

        assert len(resultado) == 1
        assert resultado[0]["titulo"] == "Lavar la loza"
        assert resultado[0]["hijo_nombre"] == "Benja"
        assert resultado[0]["url_evidencia"] == "https://foto.jpg"

    @patch("app.services.desafios_service.desafios_repo")
    @patch("app.services.desafios_service.usuarios_repo")
    def test_pendiente_de_desafio_borrado_usa_titulo_generico(self, usuarios, repo):
        usuarios.get_hijos.return_value = [{"id": "hijo-1", "nombre": "Benja"}]
        repo.get_pendientes_hijo.return_value = [
            {"id": "completado-1", "desafio_id": "desafio-borrado"}
        ]
        repo.get_by_id.return_value = []

        resultado = desafios_service.obtener_pendientes("padre-1")

        assert resultado[0]["titulo"] == "Desafío"
        assert resultado[0]["url_evidencia"] is None

    @patch("app.services.desafios_service.usuarios_repo")
    def test_con_error_devuelve_500(self, usuarios):
        usuarios.get_hijos.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            desafios_service.obtener_pendientes("padre-1")

        assert exc.value.status_code == 500


# ---------- completados, estado y eliminacion ----------

class TestOtrasOperaciones:
    @patch("app.services.desafios_service.desafios_repo")
    def test_obtener_completados_delega_en_el_repositorio(self, repo):
        repo.get_completados.return_value = [{"id": "completado-1"}]

        resultado = desafios_service.obtener_completados("hijo-1")

        repo.get_completados.assert_called_once_with("hijo-1")
        assert resultado == [{"id": "completado-1"}]

    @patch("app.services.desafios_service.desafios_repo")
    def test_actualizar_estado_delega_en_el_repositorio(self, repo):
        desafios_service.actualizar_estado("desafio-1", True)

        repo.actualizar_estado.assert_called_once_with("desafio-1", True)

    @patch("app.services.desafios_service.desafios_repo")
    def test_eliminar_desafio_exitoso(self, repo):
        resultado = desafios_service.eliminar_desafio("desafio-1")

        assert resultado == {"mensaje": "Desafío eliminado exitosamente"}
        repo.delete.assert_called_once_with("desafio-1")

    @patch("app.services.desafios_service.desafios_repo")
    def test_eliminar_con_error_devuelve_500(self, repo):
        repo.delete.side_effect = Exception("sin conexión")

        with pytest.raises(HTTPException) as exc:
            desafios_service.eliminar_desafio("desafio-1")

        assert exc.value.status_code == 500
