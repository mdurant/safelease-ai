"""
Configuración compartida: URLs internas de Django y FastAPI.
Cargar .env antes de usar (Django/FastAPI ya lo hacen en su arranque).
"""
import os
from pathlib import Path

# Cargar .env si no está cargado (p. ej. al importar desde tests o scripts)
try:
    from dotenv import load_dotenv
    _root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(_root / ".env")
    load_dotenv(_root / "infra" / ".env")
except Exception:
    pass


def get_django_internal_url() -> str:
    """URL base de Django para llamadas HTTP internas (desde FastAPI u otros)."""
    return os.getenv("DJANGO_INTERNAL_URL", "http://127.0.0.1:8000").rstrip("/")


def get_fastapi_internal_url() -> str:
    """URL base de FastAPI para llamadas HTTP internas (desde Django u otros)."""
    return os.getenv("FASTAPI_INTERNAL_URL", "http://127.0.0.1:8001").rstrip("/")
