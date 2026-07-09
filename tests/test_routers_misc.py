"""Tests de integración para canjes, ia, notificaciones, bloqueos y actividad."""
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


# ── Canjes ───────────────────────────────────────────────────────────────────

class TestCanjesRouter:
    def test_get_pendientes(self):
        with patch("app.routers.canjes.canjes_service.obtener_pendientes", return_value=[]):
            r = client.get("/canjes/pendientes/p1")
            assert r.status_code == 200

    def test_tiene_pendiente_true(self):
        with patch("app.routers.canjes.canjes_service.tiene_pendiente_hijo", return_value=True):
            r = client.get("/canjes/tiene-pendiente/h1")
            assert r.status_code == 200

    def test_tiene_pendiente_false(self):
        with patch("app.routers.canjes.canjes_service.tiene_pendiente_hijo", return_value=False):
            r = client.get("/canjes/tiene-pendiente/h1")
            assert r.status_code == 200

    def test_aprobar_canje(self):
        with patch("app.routers.canjes.canjes_service.aprobar_canje", return_value=None):
            r = client.post("/canjes/aprobar/c1")
            assert r.status_code == 200
            assert r.json()["mensaje"] == "Canje aprobado"

    def test_rechazar_canje(self):
        with patch("app.routers.canjes.canjes_service.rechazar_canje", return_value=None):
            r = client.post("/canjes/rechazar/c1")
            assert r.status_code == 200
            assert r.json()["mensaje"] == "Canje rechazado"


# ── IA ───────────────────────────────────────────────────────────────────────

class TestIARouter:
    def test_generar_desafios_exitoso(self):
        hijo = {"id": "h1", "edad": 10, "sexo": "M", "nivel_escolar": "primaria",
                "intereses": [], "personalidad": "curioso"}
        with patch("app.routers.ia.usuarios_repo.get_by_id", return_value=[hijo]), \
             patch("app.routers.ia.ia_service.generar_desafios", return_value=[{"titulo": "Reto"}]):
            r = client.post("/ia/generar", headers=_HEADERS, json={
                "categoria": "cognitiva", "hijo_id": "h1", "dificultad": "facil", "cantidad": 3
            })
            assert r.status_code == 200

    def test_generar_hijo_no_encontrado(self):
        with patch("app.routers.ia.usuarios_repo.get_by_id", return_value=[]):
            r = client.post("/ia/generar", headers=_HEADERS, json={
                "categoria": "cognitiva", "hijo_id": "fantasma", "dificultad": "facil", "cantidad": 3
            })
            assert r.status_code == 404

    def test_generar_error_500(self):
        with patch("app.routers.ia.usuarios_repo.get_by_id", side_effect=Exception("fallo")):
            r = client.post("/ia/generar", headers=_HEADERS, json={
                "categoria": "fisica", "hijo_id": "h1", "dificultad": "medio", "cantidad": 2
            })
            assert r.status_code == 500

    def test_asignar_desafio_exitoso(self):
        # desafios_repo se importa localmente dentro de la función del router
        with patch("app.repositories.desafios_repo.insertar", return_value={"id": "d1"}):
            r = client.post("/ia/asignar", headers=_HEADERS, json={
                "titulo": "Reto", "descripcion": "desc", "puntos": 10,
                "tipo": "cognitiva", "dificultad": "facil",
                "hijo_id": "h1", "esta_activo": True
            })
            assert r.status_code == 200

    def test_asignar_desafio_error_500(self):
        with patch("app.repositories.desafios_repo.insertar", side_effect=Exception("fallo bd")):
            r = client.post("/ia/asignar", headers=_HEADERS, json={
                "titulo": "Reto", "descripcion": "desc", "puntos": 10,
                "tipo": "cognitiva", "dificultad": "facil",
                "hijo_id": "h1", "esta_activo": False
            })
            assert r.status_code == 500


# ── Notificaciones ───────────────────────────────────────────────────────────

class TestNotificacionesRouter:
    def test_guardar_token(self):
        with patch("app.routers.notificaciones.registrar_fcm_token", return_value={"mensaje": "ok"}):
            r = client.post("/notificaciones/token", headers=_HEADERS, json={"fcm_token": "tok123"})
            assert r.status_code == 200

    def test_notificar_login(self):
        with patch("app.routers.notificaciones.enviar_notificacion_login", return_value={"mensaje": "ok"}):
            r = client.post("/notificaciones/login", headers=_HEADERS, json={"nombre": "Padre", "rol": "padre"})
            assert r.status_code == 200


# ── Bloqueos ─────────────────────────────────────────────────────────────────

class TestBloqueosRouter:
    def _mock_sb(self, data):
        m = MagicMock()
        m.table.return_value.insert.return_value.execute.return_value.data = [data]
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [data]
        m.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [data]
        m.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock()
        return m

    def test_crear_bloqueo_inmediato(self):
        data = {"id": "b1", "tipo": "inmediato", "hijo_id": "h1"}
        with patch("app.routers.bloqueos.supabase", self._mock_sb(data)):
            r = client.post("/bloqueos/h1", headers=_HEADERS, json={"tipo": "inmediato"})
            assert r.status_code == 200

    def test_crear_bloqueo_horario_valido(self):
        data = {"id": "b2", "tipo": "horario", "hijo_id": "h1"}
        with patch("app.routers.bloqueos.supabase", self._mock_sb(data)):
            r = client.post("/bloqueos/h1", headers=_HEADERS, json={
                "tipo": "horario", "hora_inicio": "08:00", "hora_fin": "20:00"
            })
            assert r.status_code == 200

    def test_crear_bloqueo_horario_menos_2h(self):
        with patch("app.routers.bloqueos.supabase", self._mock_sb({})):
            r = client.post("/bloqueos/h1", headers=_HEADERS, json={
                "tipo": "horario", "hora_inicio": "10:00", "hora_fin": "10:30"
            })
            assert r.status_code == 400

    def test_crear_bloqueo_horario_cruce_medianoche(self):
        data = {"id": "b3", "tipo": "horario", "hijo_id": "h1"}
        with patch("app.routers.bloqueos.supabase", self._mock_sb(data)):
            r = client.post("/bloqueos/h1", headers=_HEADERS, json={
                "tipo": "horario", "hora_inicio": "22:00", "hora_fin": "06:00"
            })
            assert r.status_code == 200

    def test_obtener_bloqueos(self):
        data = {"id": "b1", "tipo": "inmediato"}
        with patch("app.routers.bloqueos.supabase", self._mock_sb(data)):
            r = client.get("/bloqueos/h1", headers=_HEADERS)
            assert r.status_code == 200

    def test_desactivar_bloqueo(self):
        data = {"id": "b1", "activo": False}
        with patch("app.routers.bloqueos.supabase", self._mock_sb(data)):
            r = client.put("/bloqueos/b1/desactivar", headers=_HEADERS)
            assert r.status_code == 200

    def test_eliminar_bloqueo(self):
        with patch("app.routers.bloqueos.supabase", self._mock_sb({})):
            r = client.delete("/bloqueos/b1", headers=_HEADERS)
            assert r.status_code == 200

    def test_apps_bloqueadas_instante(self):
        m = MagicMock()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"package_name": "com.test"}
        ]
        with patch("app.routers.bloqueos.supabase", m):
            r = client.get("/bloqueos/h1/apps-instante", headers=_HEADERS)
            assert r.status_code == 200

    def test_apps_bloqueadas_instante_error(self):
        m = MagicMock()
        m.table.side_effect = Exception("fallo bd")
        with patch("app.routers.bloqueos.supabase", m):
            r = client.get("/bloqueos/h1/apps-instante", headers=_HEADERS)
            assert r.status_code == 500

    def test_crear_bloqueo_error_500(self):
        m = MagicMock()
        m.table.return_value.insert.return_value.execute.side_effect = Exception("fallo bd")
        with patch("app.routers.bloqueos.supabase", m):
            r = client.post("/bloqueos/h1", headers=_HEADERS, json={"tipo": "total"})
            assert r.status_code == 500


# ── Actividad ─────────────────────────────────────────────────────────────────

class TestActividadRouter:
    def test_guardar_actividad(self):
        m = MagicMock()
        m.table.return_value.upsert.return_value.execute.return_value = MagicMock()
        with patch("app.routers.actividad.supabase", m):
            r = client.post("/actividad/h1", json={
                "actividades": [{"package_name": "com.test", "minutos_uso": 15}]
            })
            assert r.status_code == 200
            assert r.json()["status"] == "success"

    def test_guardar_actividad_error_continua(self):
        m = MagicMock()
        m.table.return_value.upsert.return_value.execute.side_effect = Exception("fallo")
        with patch("app.routers.actividad.supabase", m):
            r = client.post("/actividad/h1", json={
                "actividades": [{"package_name": "com.test", "minutos_uso": 5}]
            })
            assert r.status_code == 200

    def test_obtener_actividad(self):
        m = MagicMock()
        m.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            {"package_name": "com.test", "minutos_uso": 30}
        ]
        with patch("app.routers.actividad.supabase", m):
            r = client.get("/actividad/h1")
            assert r.status_code == 200

    def test_obtener_actividad_error_500(self):
        m = MagicMock()
        m.table.side_effect = Exception("fallo bd")
        with patch("app.routers.actividad.supabase", m):
            r = client.get("/actividad/h1")
            assert r.status_code == 500
