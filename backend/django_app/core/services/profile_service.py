"""
Lógica de negocio de perfil: actualizar datos, avatar.
"""
from django.contrib.auth import get_user_model
from core.models import Perfil

User = get_user_model()


class ProfileService:
    @staticmethod
    def actualizar_perfil(usuario: User, nombre: str = None, apellido: str = None,
                          telefono: str = None, telefono_alternativo: str = None) -> Perfil:
        """Actualiza datos del perfil (nombre, apellido, teléfonos)."""
        perfil, _ = Perfil.objects.get_or_create(usuario=usuario)
        if nombre is not None:
            perfil.nombre = nombre
        if apellido is not None:
            perfil.apellido = apellido
        if telefono is not None:
            perfil.telefono = telefono
        if telefono_alternativo is not None:
            perfil.telefono_alternativo = telefono_alternativo
        perfil.save()
        return perfil

    @staticmethod
    def actualizar_avatar(usuario: User, archivo) -> Perfil:
        """Guarda avatar (ImageField)."""
        perfil, _ = Perfil.objects.get_or_create(usuario=usuario)
        if archivo:
            perfil.avatar = archivo
            perfil.save(update_fields=["avatar"])
        return perfil
