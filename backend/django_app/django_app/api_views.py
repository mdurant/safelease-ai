"""
Vistas de API interna para que FastAPI u otros servicios llamen por HTTP.
"""
from django.http import JsonResponse


def root(request):
    """GET / — ruta raíz con enlaces útiles."""
    return JsonResponse({
        "service": "safelease-ai Django",
        "admin": "/admin/",
        "api_health": "/api/health",
        "api_auth": "/api/auth/",
    })


def health(request):
    """GET /api/health — usado por FastAPI para comprobar que Django está vivo."""
    return JsonResponse({"status": "ok", "service": "django"})
