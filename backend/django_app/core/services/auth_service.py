"""
Lógica de negocio de autenticación: registro, verificación email/OTP, login, recuperación contraseña, 2FA.
"""
import hashlib
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

import pyotp
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Rol, Perfil, VerificacionEmail, VerificacionOTP, Sesion, TOTP2FA
from core.jobs import enviar_email_verificacion, enviar_otp_por_email

User = get_user_model()


class AuthService:
    """Servicio de autenticación (buenas prácticas: capa de aplicación)."""

    @staticmethod
    def _hash_codigo(codigo: str) -> str:
        return hashlib.sha256(codigo.encode()).hexdigest()

    @staticmethod
    def registrar(email: str, password: str, nombre: str = "", apellido: str = "", telefono: str = ""):
        """Crea usuario, perfil y envía email de verificación."""
        if User.objects.filter(email__iexact=email).exists():
            raise ValueError("Ya existe un usuario con ese email.")
        rol_viewer = Rol.objects.filter(codigo="viewer").first() or Rol.objects.filter(codigo="owner").first()
        with transaction.atomic():
            user = User.objects.create_user(
                email=email,
                password=password,
                rol=rol_viewer,
                verified_email=False,
                verified_phone=False,
            )
            Perfil.objects.create(
                usuario=user,
                nombre=nombre or "",
                apellido=apellido or "",
                telefono=telefono or "",
            )
            # Token verificación email (24 h)
            expira = timezone.now() + timedelta(hours=24)
            verif = VerificacionEmail.objects.create(usuario=user, expira_en=expira)
            enviar_email_verificacion(usuario=user, token=verif.token)
        return user

    @staticmethod
    def verificar_email(token: str) -> User:
        """Consume token y marca verified_email=True; opcionalmente dispara envío OTP."""
        verif = VerificacionEmail.objects.filter(token=token, usado_en__isnull=True).first()
        if not verif:
            raise ValueError("Token inválido o ya usado.")
        if timezone.now() > verif.expira_en:
            raise ValueError("Token expirado.")
        with transaction.atomic():
            verif.usado_en = timezone.now()
            verif.save(update_fields=["usado_en"])
            user = verif.usuario
            user.verified_email = True
            user.save(update_fields=["verified_email"])
            # Enviar OTP 6 dígitos (TTL 10 min)
            import random
            codigo = "".join(str(random.randint(0, 9)) for _ in range(6))
            expira_otp = timezone.now() + timedelta(minutes=10)
            VerificacionOTP.objects.create(
                usuario=user,
                codigo_hash=AuthService._hash_codigo(codigo),
                expira_en=expira_otp,
            )
            enviar_otp_por_email(usuario=user, codigo=codigo)
        return user

    @staticmethod
    def verificar_otp(usuario_id: int, codigo: str) -> User:
        """Valida código OTP 6 dígitos y marca usado."""
        user = User.objects.get(pk=usuario_id)
        codigo_hash = AuthService._hash_codigo(codigo.strip())
        verif = VerificacionOTP.objects.filter(
            usuario=user, codigo_hash=codigo_hash, usado_en__isnull=True
        ).first()
        if not verif:
            raise ValueError("Código inválido o ya usado.")
        if timezone.now() > verif.expira_en:
            raise ValueError("Código expirado.")
        verif.usado_en = timezone.now()
        verif.save(update_fields=["usado_en"])
        return user

    @staticmethod
    def tokens_para_usuario(user: User, device_id: str = "", ip: str = "", user_agent: str = ""):
        """Genera access + refresh JWT y registra sesión."""
        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        if user.rol:
            refresh["rol"] = user.rol.codigo
        access = refresh.access_token
        # Registrar sesión (opcional: guardar jti del refresh para revocar)
        Sesion.objects.create(
            usuario=user,
            device_id=device_id or "",
            ip=ip or None,
            user_agent=(user_agent or "")[:512],
            refresh_token_jti=str(refresh.get("jti", "")),
        )
        return {
            "access": str(access),
            "refresh": str(refresh),
            "access_expires": access.get("exp"),
            "user_id": user.id,
            "email": user.email,
            "rol": user.rol.codigo if user.rol else None,
        }

    @staticmethod
    def solicitar_restablecer_password(email: str) -> None:
        """Crea token y envía email con link (job)."""
        from core.models import VerificacionEmail
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return  # No revelar si existe
        expira = timezone.now() + timedelta(hours=1)
        verif = VerificacionEmail.objects.create(usuario=user, expira_en=expira)
        from core.jobs import enviar_email_restablecer_password
        enviar_email_restablecer_password(usuario=user, token=verif.token)

    @staticmethod
    def restablecer_password(token: str, nueva_password: str) -> User:
        """Consume token de restablecimiento y actualiza contraseña."""
        verif = VerificacionEmail.objects.filter(token=token, usado_en__isnull=True).first()
        if not verif:
            raise ValueError("Token inválido o ya usado.")
        if timezone.now() > verif.expira_en:
            raise ValueError("Token expirado.")
        verif.usado_en = timezone.now()
        verif.save(update_fields=["usado_en"])
        user = verif.usuario
        user.set_password(nueva_password)
        user.save(update_fields=["password"])
        return user

    @staticmethod
    def cambiar_password(user: User, password_actual: str, nueva_password: str) -> None:
        """Verifica contraseña actual y la cambia."""
        if not user.check_password(password_actual):
            raise ValueError("Contraseña actual incorrecta.")
        user.set_password(nueva_password)
        user.save(update_fields=["password"])

    @staticmethod
    def listar_sesiones(usuario: User):
        """Sesiones activas del usuario."""
        return Sesion.objects.filter(usuario=usuario).order_by("-ultima_actividad")

    @staticmethod
    def revocar_sesion(usuario: User, sesion_id: int) -> None:
        """Revoca una sesión (borrar de BD; el refresh dejará de ser válido si usamos blacklist)."""
        Sesion.objects.filter(usuario=usuario, pk=sesion_id).delete()

    @staticmethod
    def revocar_otras_sesiones(usuario: User, excluir_sesion_id: int = None) -> int:
        """Revoca todas las sesiones excepto la indicada; devuelve cantidad revocadas."""
        qs = Sesion.objects.filter(usuario=usuario)
        if excluir_sesion_id:
            qs = qs.exclude(pk=excluir_sesion_id)
        n = qs.count()
        qs.delete()
        return n

    # --- 2FA TOTP ---
    @staticmethod
    def generar_secret_2fa(usuario: User) -> dict:
        """Genera secret TOTP y URI para QR; no activa hasta verificar."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=usuario.email, issuer_name="SafeLease")
        return {"secret": secret, "provisioning_uri": provisioning_uri}

    @staticmethod
    def activar_2fa(usuario: User, secret: str, codigo: str) -> list:
        """Verifica código con secret y guarda 2FA; devuelve backup codes."""
        totp = pyotp.TOTP(secret)
        if not totp.verify(codigo, valid_window=1):
            raise ValueError("Código inválido.")
        import json
        import secrets
        backup_codes = [secrets.token_hex(4) for _ in range(8)]
        backup_hashes = [hashlib.sha256(c.encode()).hexdigest() for c in backup_codes]
        TOTP2FA.objects.update_or_create(
            usuario=usuario,
            defaults={
                "secret_cifrado": secret,  # En producción cifrar con clave de app
                "backup_codes_cifrado": json.dumps(backup_hashes),
                "activo": True,
            },
        )
        return backup_codes

    @staticmethod
    def verificar_2fa(usuario: User, codigo: str) -> bool:
        """Verifica código TOTP o backup code."""
        totp_record = TOTP2FA.objects.filter(usuario=usuario, activo=True).first()
        if not totp_record:
            return False
        totp = pyotp.TOTP(totp_record.secret_cifrado)
        if totp.verify(codigo, valid_window=1):
            return True
        import json
        try:
            hashes = json.loads(totp_record.backup_codes_cifrado or "[]")
            codigo_hash = hashlib.sha256(codigo.strip().encode()).hexdigest()
            if codigo_hash in hashes:
                hashes.remove(codigo_hash)
                totp_record.backup_codes_cifrado = json.dumps(hashes)
                totp_record.save(update_fields=["backup_codes_cifrado"])
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def desactivar_2fa(usuario: User, codigo: str) -> None:
        """Desactiva 2FA tras verificar código."""
        if not AuthService.verificar_2fa(usuario, codigo):
            raise ValueError("Código inválido.")
        TOTP2FA.objects.filter(usuario=usuario).delete()
