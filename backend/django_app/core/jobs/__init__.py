"""
Jobs de autenticación: envío de emails (verificación, OTP, restablecer password).
En desarrollo se usa backend consola; luego se puede conectar Celery/SendGrid.
"""
from .email import enviar_email_verificacion, enviar_otp_por_email, enviar_email_restablecer_password

__all__ = [
    "enviar_email_verificacion",
    "enviar_otp_por_email",
    "enviar_email_restablecer_password",
]
