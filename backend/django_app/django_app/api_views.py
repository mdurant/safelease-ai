"""
Vistas de API interna para que FastAPI u otros servicios llamen por HTTP.
"""
from django.http import JsonResponse


def health(request):
    """GET /api/health — usado por FastAPI para comprobar que Django está vivo."""
    return JsonResponse({"status": "ok", "service": "django"})
