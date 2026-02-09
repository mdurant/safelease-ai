import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

# Cliente HTTP interno para llamar a Django (shared)
from shared.config import get_django_internal_url
from shared.clients import get_django_async_client, call_django_health_async

app = FastAPI(title="safelease-ai - api")


@app.get("/")
def root():
    """Ruta raíz: enlaces útiles."""
    return {
        "service": "safelease-ai API",
        "docs": "/docs",
        "health": "/health",
        "django_status": "/django-status",
        "api_auth": "/api/auth/",
    }


# CORS para frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# Proxy de auth a Django (módulo 1): el frontend puede usar solo FastAPI como base URL
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_auth(request: Request, path: str):
    """Reenvía todas las peticiones /api/auth/* a Django."""
    django_url = get_django_internal_url().rstrip("/")
    url = f"{django_url}/api/auth/{path}"
    async with get_django_async_client() as client:
        body = await request.body()
        headers = dict(request.headers)
        headers.pop("host", None)
        try:
            r = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
            )
            if not r.content:
                return Response(status_code=r.status_code)
            ct = r.headers.get("content-type", "")
            if "application/json" in ct:
                return JSONResponse(status_code=r.status_code, content=r.json())
            return Response(status_code=r.status_code, content=r.content, media_type=ct)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error proxy auth: {e!s}")
