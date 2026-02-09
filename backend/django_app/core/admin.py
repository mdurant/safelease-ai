from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Rol, Usuario, Perfil, VerificacionEmail, VerificacionOTP, Sesion, TOTP2FA


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre")


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    fk_name = "usuario"


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ("email", "rol", "verified_email", "verified_phone", "is_staff", "date_joined")
    list_filter = ("rol", "verified_email", "is_staff")
    search_fields = ("email",)
    ordering = ("-date_joined",)
    inlines = (PerfilInline,)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permisos", {"fields": ("rol", "is_active", "is_staff", "is_superuser")}),
        ("Verificación", {"fields": ("verified_email", "verified_phone", "email_hash", "phone_hash")}),
        ("Fechas", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)


@admin.register(VerificacionEmail)
class VerificacionEmailAdmin(admin.ModelAdmin):
    list_display = ("usuario", "token", "expira_en", "usado_en")


@admin.register(VerificacionOTP)
class VerificacionOTPAdmin(admin.ModelAdmin):
    list_display = ("usuario", "expira_en", "usado_en")


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "ip", "device_id", "ultima_actividad", "creado_en")


@admin.register(TOTP2FA)
class TOTP2FAAdmin(admin.ModelAdmin):
    list_display = ("usuario", "activo", "creado_en")
