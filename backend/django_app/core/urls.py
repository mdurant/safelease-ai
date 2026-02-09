"""
URLs del módulo 1: Autenticación, perfil, sesiones, 2FA.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r"perfil", views.PerfilViewSet, basename="perfil")
router.register(r"sesiones", views.SesionesViewSet, basename="sesiones")
router.register(r"2fa", views.TwoFAViewSet, basename="2fa")

urlpatterns = [
    # Públicos
    path("registro/", views.RegistroView.as_view(), name="auth-registro"),
    path("login/", views.LoginView.as_view(), name="auth-login"),
    path("verificar-email/", views.VerificarEmailView.as_view(), name="auth-verificar-email"),
    path("verificar-otp/", views.VerificarOTPView.as_view(), name="auth-verificar-otp"),
    path("restablecer-password/solicitar/", views.SolicitarRestablecerPasswordView.as_view(), name="auth-restablecer-solicitar"),
    path("restablecer-password/", views.RestablecerPasswordView.as_view(), name="auth-restablecer"),
    # JWT refresh (SimpleJWT)
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Autenticados
    path("me/", views.MeView.as_view(), name="auth-me"),
    path("cambiar-password/", views.CambiarPasswordView.as_view(), name="auth-cambiar-password"),
    path("", include(router.urls)),
]
