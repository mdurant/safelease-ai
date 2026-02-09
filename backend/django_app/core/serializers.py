"""
Serializers para API de autenticación y perfil (módulo 1).
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Rol, Perfil, Sesion, TOTP2FA

User = get_user_model()


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ("id", "codigo", "nombre")


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ("id", "nombre", "apellido", "telefono", "telefono_alternativo", "avatar", "creado_en", "actualizado_en")
        read_only_fields = ("creado_en", "actualizado_en")


class UsuarioSerializer(serializers.ModelSerializer):
    rol_info = RolSerializer(source="rol", read_only=True)
    perfil = PerfilSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "verified_email", "verified_phone", "date_joined", "last_login",
            "rol", "rol_info", "perfil",
        )
        read_only_fields = ("id", "email", "verified_email", "verified_phone", "date_joined", "last_login", "rol")


# --- Registro / Login ---
class RegistroSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    nombre = serializers.CharField(required=False, allow_blank=True)
    apellido = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)
    aceptar_terminos = serializers.BooleanField()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese email.")
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        if not data.get("aceptar_terminos"):
            raise serializers.ValidationError({"aceptar_terminos": "Debes aceptar los términos."})
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class VerificarEmailSerializer(serializers.Serializer):
    token = serializers.CharField()


class VerificarOTPSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField()
    codigo = serializers.CharField(max_length=6, min_length=6)


# --- Password ---
class SolicitarRestablecerPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RestablecerPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    nueva_password = serializers.CharField(min_length=8, write_only=True)
    nueva_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["nueva_password"] != data["nueva_password_confirm"]:
            raise serializers.ValidationError({"nueva_password_confirm": "Las contraseñas no coinciden."})
        return data


class CambiarPasswordSerializer(serializers.Serializer):
    password_actual = serializers.CharField(write_only=True)
    nueva_password = serializers.CharField(min_length=8, write_only=True)
    nueva_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["nueva_password"] != data["nueva_password_confirm"]:
            raise serializers.ValidationError({"nueva_password_confirm": "Las contraseñas no coinciden."})
        return data


# --- Perfil ---
class ActualizarPerfilSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=False, allow_blank=True)
    apellido = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)
    telefono_alternativo = serializers.CharField(required=False, allow_blank=True)


# --- Sesiones ---
class SesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sesion
        fields = ("id", "device_id", "ip", "user_agent", "ultima_actividad", "creado_en")


# --- 2FA ---
class Activar2FASerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=6, min_length=6)


class Verificar2FASerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=10)


class Desactivar2FASerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=10)
