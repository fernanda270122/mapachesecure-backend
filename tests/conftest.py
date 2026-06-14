"""Configuración compartida para todas las pruebas.

pytest carga este archivo antes que los módulos de prueba, así que aquí
preparamos las variables de entorno antes de importar la app. Cargamos el
.env real si existe y, si falta alguna clave, ponemos un valor de respaldo:
de esa forma las pruebas corren en cualquier máquina sin secretos reales
(los servicios externos están mockeados, nunca se llaman de verdad).
"""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Interceptar el módulo supabase antes de que app.database lo importe,
# para que create_client no intente validar credenciales reales.
_mock_supabase_client = MagicMock()
_mock_supabase_module = MagicMock()
_mock_supabase_module.create_client.return_value = _mock_supabase_client
_mock_supabase_module.Client = MagicMock
sys.modules.setdefault("supabase", _mock_supabase_module)

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

os.environ.setdefault("GROQ_API_KEY", "clave-de-prueba")
os.environ.setdefault("GEMINI_API_KEY", "clave-de-prueba")
os.environ.setdefault("RESEND_API_KEY", "clave-de-prueba")
os.environ.setdefault("SUPABASE_URL", "https://prueba.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "clave-de-prueba")
