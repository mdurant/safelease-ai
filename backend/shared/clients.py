"""
Clientes HTTP para comunicación interna entre Django y FastAPI.
Usar httpx para no bloquear en async y tener timeout/retry sencillo.
"""
import httpx
from .config import get_django_internal_url, get_fastapi_internal_url

# Timeout por defecto para llamadas internas
INTERNAL_TIMEOUT = 10.0


def get_django_client() -> httpx.Client:
    """Cliente HTTP síncrono para llamar a Django (desde FastAPI sync o Django)."""
    return httpx.Client(
        base_url=get_django_internal_url(),
        timeout=INTERNAL_TIMEOUT,
        headers={"User-Agent": "safelease-ai-internal"},
    )


def get_django_async_client() -> httpx.AsyncClient:
    """Cliente HTTP asíncrono para llamar a Django (desde FastAPI async)."""
    return httpx.AsyncClient(
        base_url=get_django_internal_url(),
        timeout=INTERNAL_TIMEOUT,
        headers={"User-Agent": "safelease-ai-internal"},
    )


def get_fastapi_client() -> httpx.Client:
    """Cliente HTTP síncrono para llamar a FastAPI (desde Django)."""
    return httpx.Client(
        base_url=get_fastapi_internal_url(),
        timeout=INTERNAL_TIMEOUT,
        headers={"User-Agent": "safelease-ai-internal"},
    )


def call_django_health() -> dict:
    """Llamada de ejemplo: GET /api/health de Django. Síncrono."""
    with get_django_client() as client:
        r = client.get("/api/health")
        r.raise_for_status()
        return r.json()


async def call_django_health_async() -> dict:
    """Llamada de ejemplo: GET /api/health de Django. Asíncrono."""
    async with get_django_async_client() as client:
        r = await client.get("/api/health")
        r.raise_for_status()
        return r.json()
