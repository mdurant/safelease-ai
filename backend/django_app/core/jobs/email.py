"""
Envío de emails: verificación de cuenta, OTP, restablecer contraseña.
Automáticamente usa EMAIL_BACKEND de Django (consola en dev, SMTP en prod).
"""
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def _nombre_usuario(usuario: User) -> str:
    if hasattr(usuario, "perfil") and usuario.perfil:
        n = f"{usuario.perfil.nombre} {usuario.perfil.apellido}".strip()
        if n:
            return n
    return usuario.email


def enviar_email_verificacion(usuario: User, token: str) -> int:
    """Envía email con link de verificación (link incluye token)."""
    url = f"{getattr(settings, 'FRONTEND_VERIFY_EMAIL_URL', 'http://localhost:5173/verificar-email')}?cr={token}"
    asunto = "Verifica tu correo — SafeLease"
    mensaje = f"""
Hola {_nombre_usuario(usuario)}:

Para activar tu cuenta en SafeLease, haz clic en el siguiente enlace:

{url}

Si no has solicitado este correo, puedes ignorarlo.

Saludos,
SafeLease
"""
    return send_mail(
        asunto,
        mensaje.strip(),
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@safelease.local"),
        [usuario.email],
        fail_silently=False,
    )


def enviar_otp_por_email(usuario: User, codigo: str) -> int:
    """Envía código OTP de 6 dígitos por email."""
    asunto = "Código de verificación (6 dígitos) — SafeLease"
    mensaje = f"""
Hola {_nombre_usuario(usuario)}:

Tu código de verificación es: {codigo}

Ingresa estos 6 dígitos en la plataforma para completar la validación.
El código expira en 10 minutos.

Saludos,
SafeLease
"""
    return send_mail(
        asunto,
        mensaje.strip(),
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@safelease.local"),
        [usuario.email],
        fail_silently=False,
    )


def enviar_email_restablecer_password(usuario: User, token: str) -> int:
    """Envía email con link para restablecer contraseña."""
    url = f"{getattr(settings, 'FRONTEND_RESET_PASSWORD_URL', 'http://localhost:5173/restablecer-password')}?token={token}"
    asunto = "Restablecer contraseña — SafeLease"
    mensaje = f"""
Hola {_nombre_usuario(usuario)}:

Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace:

{url}

Si no has solicitado este correo, ignóralo.

Saludos,
SafeLease
"""
    return send_mail(
        asunto,
        mensaje.strip(),
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@safelease.local"),
        [usuario.email],
        fail_silently=False,
    )
