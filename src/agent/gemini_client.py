import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Ruta principal del proyecto
ROOT = Path(__file__).resolve().parents[2]

# Cargar variables desde .env
load_dotenv(ROOT / ".env")

def crear_cliente_gemini():
    """Crea un cliente autenticado de Gemini."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "TU_API_KEY_REAL":
        raise ValueError(
            "No se ha configurado GEMINI_API_KEY en .env"
        )

    cliente = genai.Client(api_key=api_key)

    return cliente

def obtener_modelo():
    """Devuelve el modelo configurado."""

    return os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash"
    )