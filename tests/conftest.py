"""Configuración compartida para todas las pruebas.

pytest carga este archivo antes que los módulos de prueba, así que aquí
preparamos las variables de entorno antes de importar la app. Cargamos el
.env real si existe y, si falta alguna clave, ponemos un valor de respaldo:
de esa forma las pruebas corren en cualquier máquina sin secretos reales
(los servicios externos están mockeados, nunca se llaman de verdad).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

os.environ.setdefault("GROQ_API_KEY", "clave-de-prueba")
os.environ.setdefault("GEMINI_API_KEY", "clave-de-prueba")
os.environ.setdefault("RESEND_API_KEY", "clave-de-prueba")
os.environ.setdefault("SUPABASE_URL", "https://prueba.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "clave-de-prueba")
