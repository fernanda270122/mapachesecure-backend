from unittest.mock import MagicMock, patch, call
import pytest
from fastapi import HTTPException


class TestRegistrarFcmToken:
    def test_token_registrado_correctamente(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
            from app.services.notificaciones_service import registrar_fcm_token
            result = registrar_fcm_token("uid-1", "fcm-tok-abc")
            assert result["mensaje"] == "Token FCM registrado correctamente"

    def test_error_lanza_500(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.side_effect = Exception("fallo bd")
            from app.services.notificaciones_service import registrar_fcm_token
            with pytest.raises(HTTPException) as exc:
                registrar_fcm_token("uid-1", "fcm-tok-abc")
            assert exc.value.status_code == 500


class TestEnviarNotificacionLogin:
    def test_sin_token_fcm_devuelve_mensaje(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {}
            from app.services.notificaciones_service import enviar_notificacion_login
            result = enviar_notificacion_login("uid-1", "Padre", "padre")
            assert "No hay token" in result["mensaje"]

    def test_usuario_none_devuelve_mensaje(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
            from app.services.notificaciones_service import enviar_notificacion_login
            result = enviar_notificacion_login("uid-1", "Padre", "padre")
            assert "No hay token" in result["mensaje"]

    def test_con_token_rol_padre_envia_notificacion(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb, \
             patch("app.services.notificaciones_service._init_firebase"), \
             patch("app.services.notificaciones_service.messaging") as mock_msg:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
                "fcm_token": "tok-123"
            }
            mock_msg.Message.return_value = MagicMock()
            mock_msg.send.return_value = "msg-id"
            from app.services.notificaciones_service import enviar_notificacion_login
            result = enviar_notificacion_login("uid-1", "Padre Test", "padre")
            assert "enviada" in result["mensaje"]

    def test_con_token_rol_hijo(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb, \
             patch("app.services.notificaciones_service._init_firebase"), \
             patch("app.services.notificaciones_service.messaging") as mock_msg:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
                "fcm_token": "tok-456"
            }
            mock_msg.Message.return_value = MagicMock()
            from app.services.notificaciones_service import enviar_notificacion_login
            result = enviar_notificacion_login("uid-2", "Hijo Test", "hijo")
            assert result is not None

    def test_excepcion_devuelve_mensaje_login_exitoso(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.side_effect = Exception("fallo firebase")
            from app.services.notificaciones_service import enviar_notificacion_login
            result = enviar_notificacion_login("uid-1", "Padre", "padre")
            assert "Login exitoso" in result["mensaje"]


class TestEnviarNotificacionPadre:
    def test_hijo_sin_padre_devuelve_404(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
            from app.services.notificaciones_service import enviar_notificacion_padre
            with pytest.raises(HTTPException) as exc:
                enviar_notificacion_padre("h1", "YouTube")
            assert exc.value.status_code == 404

    def test_hijo_sin_padre_id(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
                "nombre": "Hijo", "padre_id": None
            }
            from app.services.notificaciones_service import enviar_notificacion_padre
            with pytest.raises(HTTPException) as exc:
                enviar_notificacion_padre("h1", "YouTube")
            assert exc.value.status_code == 404

    def test_padre_sin_token_devuelve_404(self):
        mock_sb = MagicMock()
        hijo_data = {"nombre": "Hijo", "padre_id": "p1"}
        padre_data = {"fcm_token": None, "nombre": "Padre"}

        mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = hijo_data

        segunda_llamada = MagicMock()
        segunda_llamada.data = padre_data

        calls = [hijo_data, padre_data]
        idx = [0]

        def side_effect_data():
            val = calls[idx[0]]
            idx[0] += 1
            m = MagicMock()
            m.data = val
            return m

        with patch("app.services.notificaciones_service.supabase") as mock_sb2:
            exec_mock1 = MagicMock()
            exec_mock1.data = hijo_data
            exec_mock2 = MagicMock()
            exec_mock2.data = padre_data

            table_mock = MagicMock()
            table_mock.select.return_value.eq.return_value.single.return_value.execute.side_effect = [
                exec_mock1, exec_mock2
            ]
            mock_sb2.table.return_value = table_mock

            from app.services.notificaciones_service import enviar_notificacion_padre
            with pytest.raises(HTTPException) as exc:
                enviar_notificacion_padre("h1", "YouTube")
            assert exc.value.status_code == 404

    def test_envio_exitoso(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb, \
             patch("app.services.notificaciones_service._init_firebase"), \
             patch("app.services.notificaciones_service.messaging") as mock_msg:
            hijo_data = {"nombre": "Hijo", "padre_id": "p1"}
            padre_data = {"fcm_token": "tok-p1", "nombre": "Padre"}

            exec1 = MagicMock()
            exec1.data = hijo_data
            exec2 = MagicMock()
            exec2.data = padre_data

            table_mock = MagicMock()
            table_mock.select.return_value.eq.return_value.single.return_value.execute.side_effect = [exec1, exec2]
            mock_sb.table.return_value = table_mock
            mock_msg.Message.return_value = MagicMock()
            mock_msg.send.return_value = "ok"

            from app.services.notificaciones_service import enviar_notificacion_padre
            result = enviar_notificacion_padre("h1", "YouTube")
            assert "padre" in result["mensaje"]

    def test_excepcion_generica_devuelve_500(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.side_effect = Exception("fallo inesperado")
            from app.services.notificaciones_service import enviar_notificacion_padre
            with pytest.raises(HTTPException) as exc:
                enviar_notificacion_padre("h1", "YouTube")
            assert exc.value.status_code == 500


class TestEnviarNotificacionEvidencia:
    def test_sin_padre_imprime_y_retorna(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
            from app.services.notificaciones_service import enviar_notificacion_evidencia
            result = enviar_notificacion_evidencia("h1", "Reto")
            assert result is None

    def test_sin_padre_id(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
                "nombre": "Hijo", "padre_id": None
            }
            from app.services.notificaciones_service import enviar_notificacion_evidencia
            result = enviar_notificacion_evidencia("h1", "Reto")
            assert result is None

    def test_padre_sin_fcm_token(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            hijo_data = {"nombre": "Hijo", "padre_id": "p1"}
            padre_data = {"fcm_token": None}

            exec1 = MagicMock()
            exec1.data = hijo_data
            exec2 = MagicMock()
            exec2.data = padre_data

            table_mock = MagicMock()
            table_mock.select.return_value.eq.return_value.single.return_value.execute.side_effect = [exec1, exec2]
            mock_sb.table.return_value = table_mock

            from app.services.notificaciones_service import enviar_notificacion_evidencia
            result = enviar_notificacion_evidencia("h1", "Reto")
            assert result is None

    def test_envio_exitoso(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb, \
             patch("app.services.notificaciones_service._init_firebase"), \
             patch("app.services.notificaciones_service.messaging") as mock_msg:
            hijo_data = {"nombre": "Hijo", "padre_id": "p1"}
            padre_data = {"fcm_token": "tok-p1"}

            exec1 = MagicMock()
            exec1.data = hijo_data
            exec2 = MagicMock()
            exec2.data = padre_data

            table_mock = MagicMock()
            table_mock.select.return_value.eq.return_value.single.return_value.execute.side_effect = [exec1, exec2]
            mock_sb.table.return_value = table_mock
            mock_msg.Message.return_value = MagicMock()
            mock_msg.send.return_value = "ok"

            from app.services.notificaciones_service import enviar_notificacion_evidencia
            enviar_notificacion_evidencia("h1", "Reto importante")

    def test_excepcion_imprime_y_retorna(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.side_effect = Exception("fallo")
            from app.services.notificaciones_service import enviar_notificacion_evidencia
            enviar_notificacion_evidencia("h1", "Reto")


class TestEnviarNotificacionValidacion:
    def test_hijo_sin_token(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
            from app.services.notificaciones_service import enviar_notificacion_validacion
            enviar_notificacion_validacion("h1", True, "Reto")

    def test_aprobado_envia_notificacion(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb, \
             patch("app.services.notificaciones_service._init_firebase"), \
             patch("app.services.notificaciones_service.messaging") as mock_msg:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
                "fcm_token": "tok-h1"
            }
            mock_msg.Message.return_value = MagicMock()
            mock_msg.send.return_value = "ok"
            from app.services.notificaciones_service import enviar_notificacion_validacion
            enviar_notificacion_validacion("h1", True, "Reto ganado")

    def test_rechazado_envia_notificacion(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb, \
             patch("app.services.notificaciones_service._init_firebase"), \
             patch("app.services.notificaciones_service.messaging") as mock_msg:
            mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
                "fcm_token": "tok-h1"
            }
            mock_msg.Message.return_value = MagicMock()
            mock_msg.send.return_value = "ok"
            from app.services.notificaciones_service import enviar_notificacion_validacion
            enviar_notificacion_validacion("h1", False, "Reto fallido")

    def test_excepcion_imprime_y_retorna(self):
        with patch("app.services.notificaciones_service.supabase") as mock_sb:
            mock_sb.table.side_effect = Exception("fallo")
            from app.services.notificaciones_service import enviar_notificacion_validacion
            enviar_notificacion_validacion("h1", True, "Reto")


class TestInitFirebase:
    def test_ya_inicializado_no_hace_nada(self):
        with patch("app.services.notificaciones_service.firebase_admin") as mock_fb:
            mock_fb._apps = {"app": MagicMock()}
            from app.services.notificaciones_service import _init_firebase
            _init_firebase()
            mock_fb.initialize_app.assert_not_called()

    def test_inicializa_con_json_credentials(self):
        with patch("app.services.notificaciones_service.firebase_admin") as mock_fb, \
             patch("app.services.notificaciones_service.credentials") as mock_creds, \
             patch("app.services.notificaciones_service.os.getenv") as mock_env:
            mock_fb._apps = {}
            mock_env.return_value = '{"type": "service_account", "project_id": "test"}'
            import json
            with patch("json.loads", return_value={"type": "service_account"}):
                from app.services.notificaciones_service import _init_firebase
                _init_firebase()

    def test_inicializa_con_ruta_archivo(self):
        with patch("app.services.notificaciones_service.firebase_admin") as mock_fb, \
             patch("app.services.notificaciones_service.credentials") as mock_creds, \
             patch("app.services.notificaciones_service.os.getenv", return_value=None):
            mock_fb._apps = {}
            mock_creds.Certificate.return_value = MagicMock()
            from app.services.notificaciones_service import _init_firebase
            _init_firebase()
            mock_creds.Certificate.assert_called_once_with("firebase-credentials.json")
