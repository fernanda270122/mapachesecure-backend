from supabase import create_client, Client
from dotenv import load_dotenv
import os
from pathlib import Path

# Cargar .env con ruta explícita
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("URL:", SUPABASE_URL)  # Para verificar
print("KEY:", SUPABASE_KEY)  # Para verificar

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)