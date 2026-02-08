import os
from fastapi import FastAPI, HTTPException

# Cliente HTTP interno para llamar a Django (shared)
from shared.config import get_django_internal_url
from shared.clients import call_django_health_async

app = FastAPI(title="safelease-ai - api")


@app.get("/health")
def health():
    return {"status": "ok", "service": "fastapi"}


@app.get("/config")
def config():
    return {"fastapi_debug": os.getenv("FASTAPI_DEBUG", "0")}


@app.get("/django-status")
async def django_status():
    """
    Ejemplo de comunicación FastAPI → Django por HTTP interno.
    Llama a GET {DJANGO_INTERNAL_URL}/api/health y devuelve la respuesta.
    """
    try:
        data = await call_django_health_async()
        return {"django_url": get_django_internal_url(), "django": data}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Django no alcanzable: {e!s}. ¿Está corriendo en {get_django_internal_url()}?",
        )
