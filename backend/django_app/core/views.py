"""
Vistas API del módulo 1: Autenticación, perfil, sesiones, 2FA.
Buenas prácticas: vistas delgadas, lógica en services.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Sesion, TOTP2FA
from .serializers import (
    RegistroSerializer,
    LoginSerializer,
    VerificarEmailSerializer,
    VerificarOTPSerializer,
    SolicitarRestablecerPasswordSerializer,
    RestablecerPasswordSerializer,
    CambiarPasswordSerializer,
    UsuarioSerializer,
    ActualizarPerfilSerializer,
    PerfilSerializer,
    SesionSerializer,
    Activar2FASerializer,
    Verificar2FASerializer,
    Desactivar2FASerializer,
)
from .services import AuthService, ProfileService

User = get_user_model()


def _request_meta(request):
    """Extrae device_id, ip, user_agent del request."""
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = (x_forwarded.split(",")[0].strip() if x_forwarded else request.META.get("REMOTE_ADDR")) or ""
    return {
        "device_id": request.META.get("HTTP_X_DEVICE_ID", "")[:255],
        "ip": ip[:45] if ip else None,
        "user_agent": (request.META.get("HTTP_USER_AGENT") or "")[:512],
    }


# --- Registro (público) ---
class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegistroSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            user = AuthService.registrar(
                email=data["email"],
                password=data["password"],
                nombre=data.get("nombre", ""),
                apellido=data.get("apellido", ""),
                telefono=data.get("telefono", ""),
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Cuenta creada. Revisa tu correo para verificar.", "email": user.email},
            status=status.HTTP_201_CREATED,
        )


# --- Verificación email (público) ---
class VerificarEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = VerificarEmailSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            user = AuthService.verificar_email(ser.validated_data["token"])
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "detail": "Email verificado. Revisa tu correo para el código de 6 dígitos.",
            "usuario_id": user.id,
            "email": user.email,
        })


# --- Verificación OTP (público) ---
class VerificarOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = VerificarOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            user = AuthService.verificar_otp(usuario_id=data["usuario_id"], codigo=data["codigo"])
        except (ValueError, User.DoesNotExist) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        meta = _request_meta(request)
        tokens = AuthService.tokens_para_usuario(user, **meta)
        return Response(tokens, status=status.HTTP_200_OK)


# --- Login (público) ---
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"]
        password = ser.validated_data["password"]
        user = User.objects.filter(email__iexact=email).first()
        if not user or not user.check_password(password):
            return Response({"detail": "Credenciales incorrectas."}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"detail": "Cuenta desactivada."}, status=status.HTTP_403_FORBIDDEN)
        meta = _request_meta(request)
        tokens = AuthService.tokens_para_usuario(user, **meta)
        return Response(tokens)


# --- JWT refresh (SimpleJWT) se usa desde el frontend con el refresh token ---
# Se expone vía path api/auth/token/refresh (ver urls)


# --- Restablecer contraseña (público) ---
class SolicitarRestablecerPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = SolicitarRestablecerPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        AuthService.solicitar_restablecer_password(ser.validated_data["email"])
        return Response({"detail": "Si el email existe, recibirás un enlace para restablecer la contraseña."})


class RestablecerPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RestablecerPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            AuthService.restablecer_password(data["token"], data["nueva_password"])
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Contraseña actualizada. Ya puedes iniciar sesión."})


# --- Usuario actual (autenticado) ---
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ser = UsuarioSerializer(request.user)
        return Response(ser.data)


# --- Cambiar contraseña (autenticado) ---
class CambiarPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = CambiarPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            AuthService.cambiar_password(
                request.user,
                data["password_actual"],
                data["nueva_password"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Contraseña actualizada."})


# --- Perfil (autenticado) ---
class PerfilViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return None

    def list(self, request):
        """GET /api/auth/perfil/ — datos del perfil del usuario actual."""
        perfil = getattr(request.user, "perfil", None)
        if not perfil:
            return Response({}, status=status.HTTP_200_OK)
        ser = PerfilSerializer(perfil)
        return Response(ser.data)

    @action(detail=False, methods=["patch", "put"])
    def actualizar(self, request):
        """PATCH /api/auth/perfil/actualizar/ — actualizar nombre, apellido, teléfonos."""
        ser = ActualizarPerfilSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ProfileService.actualizar_perfil(request.user, **ser.validated_data)
        perfil = getattr(request.user, "perfil", None)
        if perfil:
            perfil.refresh_from_db()
        return Response(PerfilSerializer(perfil).data if perfil else {})

    @action(detail=False, methods=["post"], url_path="avatar")
    def avatar(self, request):
        """POST /api/auth/perfil/avatar/ — subir avatar."""
        archivo = request.FILES.get("avatar")
        if not archivo:
            return Response({"detail": "Falta el archivo 'avatar'."}, status=status.HTTP_400_BAD_REQUEST)
        ProfileService.actualizar_avatar(request.user, archivo)
        perfil = getattr(request.user, "perfil", None)
        return Response(PerfilSerializer(perfil).data if perfil else {})


# --- Sesiones (autenticado) ---
class SesionesViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Sesion.objects.filter(usuario=self.request.user)

    def list(self, request):
        """GET /api/auth/sesiones/ — listar sesiones activas."""
        qs = self.get_queryset().order_by("-ultima_actividad")
        ser = SesionSerializer(qs, many=True)
        return Response(ser.data)

    @action(detail=True, methods=["post"], url_path="revocar")
    def revocar(self, request, pk=None):
        """POST /api/auth/sesiones/<id>/revocar/ — revocar una sesión."""
        try:
            AuthService.revocar_sesion(request.user, int(pk))
        except Exception:
            return Response({"detail": "Sesión no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Sesión revocada."})

    @action(detail=False, methods=["post"], url_path="revocar-otras")
    def revocar_otras(self, request):
        """POST /api/auth/sesiones/revocar-otras/ — revocar todas excepto la actual (por jti no implementado aquí, revoca todas)."""
        n = AuthService.revocar_otras_sesiones(request.user)
        return Response({"detail": f"Se revocaron {n} sesión(es)."})


# --- 2FA (autenticado) ---
class TwoFAViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return None

    @action(detail=False, methods=["get"], url_path="setup")
    def setup(self, request):
        """GET /api/auth/2fa/setup/ — obtener secret y URI para QR (activar 2FA)."""
        data = AuthService.generar_secret_2fa(request.user)
        return Response(data)

    @action(detail=False, methods=["post"], url_path="activar")
    def activar(self, request):
        """POST /api/auth/2fa/activar/ — activar 2FA con secret + código."""
        # Secret viene del paso setup (frontend lo guarda temporalmente)
        secret = request.data.get("secret")
        if not secret:
            return Response({"detail": "Falta 'secret'."}, status=status.HTTP_400_BAD_REQUEST)
        ser = Activar2FASerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            backup_codes = AuthService.activar_2fa(
                request.user,
                secret=secret,
                codigo=ser.validated_data["codigo"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "2FA activado.", "backup_codes": backup_codes})

    @action(detail=False, methods=["get"], url_path="estado")
    def estado(self, request):
        """GET /api/auth/2fa/estado/ — saber si el usuario tiene 2FA activo."""
        tiene = TOTP2FA.objects.filter(usuario=request.user, activo=True).exists()
        return Response({"tiene_2fa": tiene})

    @action(detail=False, methods=["post"], url_path="desactivar")
    def desactivar(self, request):
        """POST /api/auth/2fa/desactivar/ — desactivar 2FA (requiere código)."""
        ser = Desactivar2FASerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            AuthService.desactivar_2fa(request.user, ser.validated_data["codigo"])
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "2FA desactivado."})
