"""
Modelos del módulo 1: Identidad y Acceso.
Ref: docs/MODULOS-TECNICOS.md — core_rol, core_usuario, core_perfil, etc.
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


def _default_token():
    return str(uuid.uuid4())


class Rol(models.Model):
    """Rol de usuario: owner (publica), viewer (navega), admin (moderación)."""
    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=64)

    class Meta:
        db_table = "core_rol"
        ordering = ["id"]

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        rol_admin = Rol.objects.filter(codigo="admin").first()
        if rol_admin:
            extra_fields.setdefault("rol", rol_admin)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Usuario: email como identificador; roles; verificación email/teléfono."""
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)
    verified_email = models.BooleanField(default=False)
    verified_phone = models.BooleanField(default=False)
    # Hashes para privacidad/auditoría (opcional: email_hash, phone_hash)
    email_hash = models.CharField(max_length=64, blank=True)
    phone_hash = models.CharField(max_length=64, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        db_table = "core_usuario"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email


class Perfil(models.Model):
    """Datos del publicador: nombre, apellido, teléfono, avatar (KYC lite opcional)."""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil")
    nombre = models.CharField(max_length=128, blank=True)
    apellido = models.CharField(max_length=128, blank=True)
    telefono = models.CharField(max_length=32, blank=True)
    telefono_alternativo = models.CharField(max_length=32, blank=True)
    avatar = models.ImageField(upload_to="avatares/%Y/%m/", null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_perfil"

    def __str__(self):
        return f"{self.nombre} {self.apellido}".strip() or self.usuario.email


class VerificacionEmail(models.Model):
    """Token de verificación de email (link con expiración)."""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="verificaciones_email")
    token = models.CharField(max_length=64, unique=True, default=_default_token, editable=False)
    expira_en = models.DateTimeField()
    usado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "core_verificacion_email"
        ordering = ["-expira_en"]


class VerificacionOTP(models.Model):
    """Código OTP 6 dígitos post-verificación email (TTL corto)."""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="verificaciones_otp")
    codigo_hash = models.CharField(max_length=128)  # hash del código de 6 dígitos
    expira_en = models.DateTimeField()
    usado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "core_verificacion_otp"
        ordering = ["-expira_en"]


class Sesion(models.Model):
    """Sesión activa: device, IP, refresh token (para listar/revocar)."""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="sesiones")
    device_id = models.CharField(max_length=255, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    refresh_token_jti = models.CharField(max_length=255, blank=True)  # JWT ID del refresh token
    ultima_actividad = models.DateTimeField(auto_now=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_sesion"
        ordering = ["-ultima_actividad"]


class TOTP2FA(models.Model):
    """2FA TOTP: secret cifrado y códigos de respaldo."""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="totp_2fa")
    secret_cifrado = models.CharField(max_length=255)
    backup_codes_cifrado = models.TextField(blank=True)  # JSON de códigos hasheados
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_totp_2fa"
