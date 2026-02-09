"""
Seeder del módulo 1: roles y usuario demo.
Contraseña por defecto: password (solo en desarrollo).
Ejecutar después de: python manage.py migrate
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import ProgrammingError
from django.contrib.auth import get_user_model
from core.models import Rol, Perfil

User = get_user_model()


ROLES = [
    {"codigo": "owner", "nombre": "Publicador"},
    {"codigo": "viewer", "nombre": "Navegante"},
    {"codigo": "admin", "nombre": "Administrador"},
]

USUARIO_DEMO = {
    "email": "demo@safelease.local",
    "password": "password",
    "nombre": "Usuario",
    "apellido": "Demo",
}


class Command(BaseCommand):
    help = "Crea roles y usuario demo (password por defecto: password)."

    def handle(self, *args, **options):
        # Comprobar que las tablas existen (migrate aplicado)
        try:
            Rol.objects.exists()
        except ProgrammingError:
            raise CommandError(
                "Las tablas de core no existen. Ejecuta primero: python manage.py migrate"
            )
        # Roles
        for r in ROLES:
            _, created = Rol.objects.get_or_create(codigo=r["codigo"], defaults={"nombre": r["nombre"]})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Rol creado: {r['codigo']}"))
        # Usuario demo
        rol_owner = Rol.objects.get(codigo="owner")
        user, created = User.objects.get_or_create(
            email=USUARIO_DEMO["email"],
            defaults={
                "rol": rol_owner,
                "verified_email": True,
                "verified_phone": False,
                "is_active": True,
            },
        )
        if created:
            user.set_password(USUARIO_DEMO["password"])
            user.save()
            Perfil.objects.get_or_create(
                usuario=user,
                defaults={
                    "nombre": USUARIO_DEMO["nombre"],
                    "apellido": USUARIO_DEMO["apellido"],
                },
            )
            self.stdout.write(self.style.SUCCESS(
                f"Usuario demo creado: {USUARIO_DEMO['email']} / password={USUARIO_DEMO['password']}"
            ))
        else:
            # Asegurar que la contraseña sea la por defecto si se vuelve a ejecutar
            if not user.check_password(USUARIO_DEMO["password"]):
                user.set_password(USUARIO_DEMO["password"])
                user.save()
                self.stdout.write(self.style.WARNING("Contraseña del usuario demo restablecida a 'password'."))
        self.stdout.write(self.style.SUCCESS("Seed de autenticación completado."))
