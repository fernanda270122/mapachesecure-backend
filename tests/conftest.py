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

# Mockear paquetes pesados antes de cualquier import de la app.
# Así los tests corren sin instalar supabase, firebase-admin, groq ni resend.

_mock_supabase_client = MagicMock()
_mock_supabase_module = MagicMock()
_mock_supabase_module.create_client.return_value = _mock_supabase_client
_mock_supabase_module.Client = MagicMock
sys.modules.setdefault("supabase", _mock_supabase_module)

sys.modules.setdefault("resend", MagicMock())

sys.modules.setdefault("groq", MagicMock())

_mock_firebase = MagicMock()
sys.modules.setdefault("firebase_admin", _mock_firebase)
sys.modules.setdefault("firebase_admin.credentials", MagicMock())
sys.modules.setdefault("firebase_admin.messaging", MagicMock())

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

os.environ.setdefault("GROQ_API_KEY", "clave-de-prueba")
os.environ.setdefault("GEMINI_API_KEY", "clave-de-prueba")
os.environ.setdefault("RESEND_API_KEY", "clave-de-prueba")
os.environ.setdefault("SUPABASE_URL", "https://prueba.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "clave-de-prueba")
