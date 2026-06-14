"""Pruebas unitarias de ia_service.

El cliente de Groq se reemplaza con un mock: ninguna prueba llama a la API
de IA real ni gasta la API key.
"""
import json
from unittest.mock import MagicMock, patch

from app.services import ia_service


def _respuesta_groq(contenido):
    """Simula la respuesta de client.chat.completions.create de Groq."""
    respuesta = MagicMock()
    respuesta.choices[0].message.content = contenido
    return respuesta


def _json_desafios():
    return json.dumps({
        "desafios": [
            {"titulo": "Reciclar en casa", "descripcion": "Paso 1... Paso 2...",
             "puntos": 10, "tiempo_estimado_minutos": 5}
        ]
    })


# ---------- parseo de la respuesta ----------

class TestGenerarDesafios:
    @patch("app.services.ia_service.client")
    def test_devuelve_el_json_parseado(self, client):
        client.chat.completions.create.return_value = _respuesta_groq(_json_desafios())

        resultado = ia_service.generar_desafios("ciencia", edad=10, dificultad="facil")

        assert "desafios" in resultado
        assert resultado["desafios"][0]["titulo"] == "Reciclar en casa"

    @patch("app.services.ia_service.client")
    def test_limpia_el_json_envuelto_en_bloque_de_codigo(self, client):
        envuelto = f"```json\n{_json_desafios()}\n```"
        client.chat.completions.create.return_value = _respuesta_groq(envuelto)

        resultado = ia_service.generar_desafios("ciencia", edad=10, dificultad="facil")

        assert resultado["desafios"][0]["puntos"] == 10

    @patch("app.services.ia_service.client")
    def test_limpia_el_bloque_de_codigo_sin_etiqueta_json(self, client):
        envuelto = f"```\n{_json_desafios()}\n```"
        client.chat.completions.create.return_value = _respuesta_groq(envuelto)

        resultado = ia_service.generar_desafios("ciencia", edad=10, dificultad="facil")

        assert "desafios" in resultado


# ---------- armado del contexto del nino ----------

class TestContextoDelPrompt:
    def _prompt_enviado(self, client):
        """Extrae el prompt de usuario que se mandó a Groq."""
        mensajes = client.chat.completions.create.call_args.kwargs["messages"]
        return mensajes[1]["content"]

    @patch("app.services.ia_service.client")
    def test_sexo_femenino_usa_nina(self, client):
        client.chat.completions.create.return_value = _respuesta_groq(_json_desafios())

        ia_service.generar_desafios("arte", edad=8, dificultad="facil", sexo="femenino")

        assert "una niña de 8 años" in self._prompt_enviado(client)

    @patch("app.services.ia_service.client")
    def test_sexo_masculino_usa_nino(self, client):
        client.chat.completions.create.return_value = _respuesta_groq(_json_desafios())

        ia_service.generar_desafios("arte", edad=8, dificultad="facil", sexo="masculino")

        assert "niño de 8 años" in self._prompt_enviado(client)

    @patch("app.services.ia_service.client")
    def test_incluye_intereses_y_personalidad_en_el_prompt(self, client):
        client.chat.completions.create.return_value = _respuesta_groq(_json_desafios())

        ia_service.generar_desafios(
            "deporte", edad=12, dificultad="medio",
            nivel_escolar="básica", intereses=["fútbol", "música"], personalidad="activo",
        )

        prompt = self._prompt_enviado(client)
        assert "nivel escolar básica" in prompt
        assert "fútbol, música" in prompt
        assert "personalidad activo" in prompt

    @patch("app.services.ia_service.client")
    def test_respeta_la_categoria_y_cantidad_pedidas(self, client):
        client.chat.completions.create.return_value = _respuesta_groq(_json_desafios())

        ia_service.generar_desafios("ciencia", edad=10, dificultad="dificil", cantidad=5)

        prompt = self._prompt_enviado(client)
        assert 'categoría "ciencia"' in prompt
        assert "exactamente 5 desafíos" in prompt
