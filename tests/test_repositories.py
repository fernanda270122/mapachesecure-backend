"""Tests de repositorios — cubre las líneas que llaman a supabase directamente."""
from unittest.mock import MagicMock, patch


def _sb():
    return MagicMock()


# ── apps_repo ────────────────────────────────────────────────────────────────

class TestAppsRepo:
    def test_get_by_hijo(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "a1"}]
        with patch("app.repositories.apps_repo.supabase", m):
            from app.repositories import apps_repo
            result = apps_repo.get_by_hijo("h1")
            assert result == [{"id": "a1"}]

    def test_create(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value.data = [{"id": "a1"}]
        with patch("app.repositories.apps_repo.supabase", m):
            from app.repositories import apps_repo
            result = apps_repo.create({"package_name": "com.test"})
            assert result["id"] == "a1"

    def test_delete(self):
        m = _sb()
        with patch("app.repositories.apps_repo.supabase", m):
            from app.repositories import apps_repo
            apps_repo.delete("a1")
            m.table.return_value.delete.return_value.eq.return_value.execute.assert_called_once()

    def test_get_by_hijo_y_package(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.apps_repo.supabase", m):
            from app.repositories import apps_repo
            result = apps_repo.get_by_hijo_y_package("h1", "com.test")
            assert result == []

    def test_get_uso_hoy(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.apps_repo.supabase", m):
            from app.repositories import apps_repo
            result = apps_repo.get_uso_hoy("h1", "2026-06-19")
            assert result == []

    def test_crear_uso(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value.data = [{"id": "u1"}]
        with patch("app.repositories.apps_repo.supabase", m):
            from app.repositories import apps_repo
            result = apps_repo.crear_uso({"hijo_id": "h1", "minutos_usados": 30})
            assert result["id"] == "u1"

    def test_actualizar_uso(self):
        m = _sb()
        m.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "u1"}]
        with patch("app.repositories.apps_repo.supabase", m):
            from app.repositories import apps_repo
            result = apps_repo.actualizar_uso("u1", 60)
            assert result == [{"id": "u1"}]

    def test_update(self):
        m = _sb()
        m.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "a1"}]
        with patch("app.repositories.apps_repo.supabase", m):
            from app.repositories import apps_repo
            result = apps_repo.update("a1", {"requiere_desafio": False})
            assert result == [{"id": "a1"}]


# ── auth_repo ────────────────────────────────────────────────────────────────

class TestAuthRepo:
    def test_sign_up(self):
        m = _sb()
        m.auth.sign_up.return_value = MagicMock(user=MagicMock(id="u1"))
        with patch("app.repositories.auth_repo.supabase", m):
            from app.repositories import auth_repo
            result = auth_repo.sign_up("test@test.com", "pass123")
            assert result.user.id == "u1"

    def test_admin_create_user(self):
        m = _sb()
        m.auth.admin.create_user.return_value = MagicMock(user=MagicMock(id="u2"))
        with patch("app.repositories.auth_repo.supabase", m):
            from app.repositories import auth_repo
            result = auth_repo.admin_create_user("hijo@test.com", "pass123")
            assert result.user.id == "u2"

    def test_sign_in(self):
        m = _sb()
        m.auth.sign_in_with_password.return_value = MagicMock(user=MagicMock(id="u1"))
        with patch("app.repositories.auth_repo.supabase", m):
            from app.repositories import auth_repo
            result = auth_repo.sign_in("test@test.com", "pass123")
            assert result.user.id == "u1"

    def test_sign_out(self):
        m = _sb()
        with patch("app.repositories.auth_repo.supabase", m):
            from app.repositories import auth_repo
            auth_repo.sign_out()
            m.auth.sign_out.assert_called_once()

    def test_create_perfil(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value = MagicMock()
        with patch("app.repositories.auth_repo.supabase", m):
            from app.repositories import auth_repo
            auth_repo.create_perfil({"id": "u1", "nombre": "Test"})

    def test_get_perfil(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "u1"}]
        with patch("app.repositories.auth_repo.supabase", m):
            from app.repositories import auth_repo
            result = auth_repo.get_perfil("u1")
            assert result == [{"id": "u1"}]

    def test_vincular_hijo(self):
        m = _sb()
        m.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "h1"}]
        with patch("app.repositories.auth_repo.supabase", m):
            from app.repositories import auth_repo
            result = auth_repo.vincular_hijo("h1", "p1")
            assert result == [{"id": "h1"}]

    def test_reset_password(self):
        m = _sb()
        with patch("app.repositories.auth_repo.supabase", m):
            from app.repositories import auth_repo
            auth_repo.reset_password("test@test.com")
            m.auth.reset_password_for_email.assert_called_once()

    def test_cambiar_password(self):
        m = _sb()
        m.auth.get_user.return_value = MagicMock(user=MagicMock(id="u1"))
        m.auth.admin.update_user_by_id.return_value = MagicMock()
        with patch("app.repositories.auth_repo.supabase", m):
            from app.repositories import auth_repo
            auth_repo.cambiar_password("tok", "nueva")
            m.auth.admin.update_user_by_id.assert_called_once()


# ── canjes_repo ──────────────────────────────────────────────────────────────

class TestCanjesRepo:
    def test_obtener_canjes_pendientes_sin_hijos(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.canjes_repo.supabase", m):
            from app.repositories import canjes_repo
            result = canjes_repo.obtener_canjes_pendientes("p1")
            assert result == []

    def test_obtener_canjes_pendientes_con_hijos(self):
        m = _sb()
        exec1 = MagicMock()
        exec1.data = [{"id": "h1"}, {"id": "h2"}]
        exec2 = MagicMock()
        exec2.data = [{"id": "c1", "estado": "pendiente"}]

        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.execute.return_value = exec1
        table_mock.select.return_value.in_.return_value.eq.return_value.execute.return_value = exec2
        m.table.return_value = table_mock

        with patch("app.repositories.canjes_repo.supabase", m):
            from app.repositories import canjes_repo
            result = canjes_repo.obtener_canjes_pendientes("p1")
            assert isinstance(result, list)

    def test_tiene_pendiente_true(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{"id": "c1"}]
        with patch("app.repositories.canjes_repo.supabase", m):
            from app.repositories import canjes_repo
            assert canjes_repo.tiene_pendiente("h1") is True

    def test_tiene_pendiente_false(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.canjes_repo.supabase", m):
            from app.repositories import canjes_repo
            assert canjes_repo.tiene_pendiente("h1") is False

    def test_obtener_pendiente_por_id_existe(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "c1"}]
        with patch("app.repositories.canjes_repo.supabase", m):
            from app.repositories import canjes_repo
            result = canjes_repo.obtener_pendiente_de_hijo_por_id("c1")
            assert result["id"] == "c1"

    def test_obtener_pendiente_por_id_no_existe(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.canjes_repo.supabase", m):
            from app.repositories import canjes_repo
            result = canjes_repo.obtener_pendiente_de_hijo_por_id("fantasma")
            assert result is None

    def test_actualizar_estado_canje(self):
        m = _sb()
        with patch("app.repositories.canjes_repo.supabase", m):
            from app.repositories import canjes_repo
            canjes_repo.actualizar_estado_canje("c1", "aprobado")
            m.table.return_value.update.return_value.eq.return_value.execute.assert_called_once()


# ── catalogo_repo ────────────────────────────────────────────────────────────

class TestCatalogoRepo:
    def test_get_all(self):
        m = _sb()
        m.table.return_value.select.return_value.order.return_value.execute.return_value.data = [{"id": "cat1"}]
        with patch("app.repositories.catalogo_repo.supabase", m):
            from app.repositories import catalogo_repo
            result = catalogo_repo.get_all()
            assert result == [{"id": "cat1"}]

    def test_create(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value.data = [{"id": "cat1"}]
        with patch("app.repositories.catalogo_repo.supabase", m):
            from app.repositories import catalogo_repo
            result = catalogo_repo.create({"nombre": "Helado"})
            assert result == {"id": "cat1"}

    def test_get_by_id(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "cat1"}]
        with patch("app.repositories.catalogo_repo.supabase", m):
            from app.repositories import catalogo_repo
            result = catalogo_repo.get_by_id("cat1")
            assert result == [{"id": "cat1"}]

    def test_delete(self):
        m = _sb()
        m.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.catalogo_repo.supabase", m):
            from app.repositories import catalogo_repo
            result = catalogo_repo.delete("cat1", "p1")
            assert result == []


# ── usuarios_repo ────────────────────────────────────────────────────────────

class TestUsuariosRepo:
    def test_get_all(self):
        m = _sb()
        m.table.return_value.select.return_value.execute.return_value.data = [{"id": "u1"}]
        with patch("app.repositories.usuarios_repo.supabase", m):
            from app.repositories import usuarios_repo
            result = usuarios_repo.get_all()
            assert result == [{"id": "u1"}]

    def test_get_by_id(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "u1"}]
        with patch("app.repositories.usuarios_repo.supabase", m):
            from app.repositories import usuarios_repo
            result = usuarios_repo.get_by_id("u1")
            assert result == [{"id": "u1"}]

    def test_create(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value.data = [{"id": "u1"}]
        with patch("app.repositories.usuarios_repo.supabase", m):
            from app.repositories import usuarios_repo
            result = usuarios_repo.create({"nombre": "Test", "rol": "padre"})
            assert result == {"id": "u1"}

    def test_get_hijos(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.usuarios_repo.supabase", m):
            from app.repositories import usuarios_repo
            result = usuarios_repo.get_hijos("p1")
            assert result == []

    def test_update(self):
        m = _sb()
        m.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "u1"}]
        with patch("app.repositories.usuarios_repo.supabase", m):
            from app.repositories import usuarios_repo
            result = usuarios_repo.update("u1", {"nombre": "Nuevo"})
            assert result == [{"id": "u1"}]

    def test_delete(self):
        m = _sb()
        m.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.usuarios_repo.supabase", m):
            from app.repositories import usuarios_repo
            result = usuarios_repo.delete("u1")
            assert result == []


# ── desafios_repo ────────────────────────────────────────────────────────────

class TestDesafiosRepo:
    def test_get_all(self):
        m = _sb()
        m.table.return_value.select.return_value.execute.return_value.data = [{"id": "d1"}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.get_all()
            assert result == [{"id": "d1"}]

    def test_get_by_hijo(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "d1"}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.get_by_hijo("h1")
            assert result == [{"id": "d1"}]

    def test_get_by_tipo(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "d1"}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.get_by_tipo("cognitivo")
            assert result == [{"id": "d1"}]

    def test_get_by_id(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "d1"}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.get_by_id("d1")
            assert result == [{"id": "d1"}]

    def test_registrar_completado(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value.data = [{"id": "dc1"}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.registrar_completado({"hijo_id": "h1", "desafio_id": "d1"})
            assert result == {"id": "dc1"}

    def test_get_completados(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.get_completados("h1")
            assert result == []

    def test_get_puntos(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"total": 30}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.get_puntos("h1")
            assert result == [{"total": 30}]

    def test_get_completado_by_id(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "dc1"}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.get_completado_by_id("dc1")
            assert result == [{"id": "dc1"}]

    def test_actualizar_completado(self):
        m = _sb()
        m.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "dc1"}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.actualizar_completado("dc1", {"validado": True})
            assert result == [{"id": "dc1"}]

    def test_get_pendientes_hijo(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.get_pendientes_hijo("h1")
            assert result == []

    def test_actualizar_estado(self):
        m = _sb()
        m.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "d1"}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.actualizar_estado("d1", True)
            assert result == [{"id": "d1"}]

    def test_insertar(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value.data = [{"id": "d1"}]
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.insertar({"titulo": "Reto"})
            assert result == [{"id": "d1"}]

    def test_delete_completado(self):
        m = _sb()
        m.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.delete_completado("dc1")
            assert result == []

    def test_delete(self):
        m = _sb()
        m.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.desafios_repo.supabase", m):
            from app.repositories import desafios_repo
            result = desafios_repo.delete("d1")
            assert result == []


# ── recompensas_repo ─────────────────────────────────────────────────────────

class TestRecompensasRepo:
    def test_get_by_hijo(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            result = recompensas_repo.get_by_hijo("h1")
            assert result == []

    def test_create(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value.data = [{"id": "r1"}]
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            result = recompensas_repo.create({"titulo": "Premio"})
            assert result == {"id": "r1"}

    def test_get_by_hijo_y_titulo(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            result = recompensas_repo.get_by_hijo_y_titulo("h1", "Premio")
            assert result == []

    def test_get_by_id(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "r1"}]
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            result = recompensas_repo.get_by_id("r1")
            assert result == [{"id": "r1"}]

    def test_registrar_canje(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value.data = [{"id": "c1"}]
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            result = recompensas_repo.registrar_canje({"hijo_id": "h1", "recompensa_id": "r1"})
            assert result == {"id": "c1"}

    def test_get_historial_canjes(self):
        m = _sb()
        m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            result = recompensas_repo.get_historial_canjes("h1")
            assert result == []

    def test_get_catalogo(self):
        m = _sb()
        m.table.return_value.select.return_value.execute.return_value.data = []
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            result = recompensas_repo.get_catalogo()
            assert result == []

    def test_create_catalogo(self):
        m = _sb()
        m.table.return_value.insert.return_value.execute.return_value.data = [{"id": "cat1"}]
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            result = recompensas_repo.create_catalogo({"nombre": "Helado"})
            assert result == [{"id": "cat1"}]

    def test_update(self):
        m = _sb()
        m.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "r1"}]
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            result = recompensas_repo.update("r1", {"disponible": False})
            assert result == [{"id": "r1"}]

    def test_deshabilitar_todas(self):
        m = _sb()
        with patch("app.repositories.recompensas_repo.supabase", m):
            from app.repositories import recompensas_repo
            recompensas_repo.deshabilitar_todas("h1")
            m.table.return_value.update.return_value.eq.return_value.execute.assert_called_once()
