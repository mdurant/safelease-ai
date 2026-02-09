# Módulo 1 — Autenticación (Setup y uso)

Backend: **Django** (modelos, servicios, API REST, JWT) + **FastAPI** (proxy opcional y CORS).  
Frontend: **React** (Vite, TypeScript).

Contraseña por defecto del usuario demo: **`password`**.

---

## 1. Backend (Django + FastAPI)

### Dependencias

```bash
cd /Users/mdurant/proyectos/safelease-ai
pip install -r requirements.txt
```

### Base de datos y migraciones

Asegúrate de tener PostgreSQL en marcha (o usa Docker). Luego:

```bash
cd backend/django_app
python manage.py makemigrations core
python manage.py migrate
```

(Si ya existían migraciones de `auth` o `contenttypes`, Django puede pedir que especifiques `--run-syncdb` o que crees el superusuario después. El orden correcto es: primero migrar `core`, que incluye el usuario personalizado.)

### Seed (roles + usuario demo)

```bash
python manage.py seed_auth
```

Esto crea:

- Roles: **owner** (Publicador), **viewer** (Navegante), **admin** (Administrador).
- Usuario demo: **demo@safelease.local** con contraseña **password**.

### Ejecutar backend

**Terminal 1 — Django:**

```bash
cd backend/django_app
python manage.py runserver 8000
```

**Terminal 2 — FastAPI (opcional; el frontend puede hablar solo con Django):**

```bash
cd backend/fastapi_app
uvicorn main:app --reload --port 8001
```

Si usas solo Django para auth, el frontend puede apuntar a `http://localhost:8000` (y quitar el proxy de Vite o configurarlo a 8000).

---

## 2. Frontend (React)

### Instalación y ejecución

```bash
cd frontend
npm install
npm run dev
```

Abre **http://localhost:5173**.

El `vite.config.ts` hace proxy de `/api` a `http://127.0.0.1:8001`. Si quieres que el frontend hable solo con Django, cambia el proxy a `http://127.0.0.1:8000` y las peticiones irán a `http://localhost:8000/api/auth/...`.

### Flujos disponibles

| Ruta | Descripción |
|------|-------------|
| `/ingresar` | Login (email + contraseña) |
| `/registro` | Crear cuenta → envío de email de verificación |
| `/verificar-email?cr=<token>` | Verificación de email (link del correo) |
| `/verificar-otp?usuario_id=<id>` | Código OTP 6 dígitos (tras verificar email) |
| `/dashboard` | Dashboard (requiere auth) |
| `/perfil` | Perfil (nombre, apellido, teléfonos, avatar) |
| `/cambiar-password` | Cambio de contraseña |
| `/sesiones` | Sesiones activas y revocar |
| `/2fa` | Activar/desactivar 2FA TOTP |
| `/restablecer-password` | Solicitar enlace o restablecer con token |

---

## 3. API (Django)

Base: **http://localhost:8000/api/auth/** (o vía FastAPI proxy: http://localhost:8001/api/auth/).

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/registro/` | No | Registro (email, password, nombre, apellido, telefono, aceptar_terminos) |
| POST | `/login/` | No | Login → `{ access, refresh, user_id, email, rol }` |
| POST | `/verificar-email/` | No | Body: `{ token }` |
| POST | `/verificar-otp/` | No | Body: `{ usuario_id, codigo }` → tokens |
| POST | `/token/refresh/` | No | Body: `{ refresh }` → `{ access }` |
| GET | `/me/` | JWT | Usuario actual |
| POST | `/cambiar-password/` | JWT | Body: `password_actual`, `nueva_password`, `nueva_password_confirm` |
| GET | `/perfil/` | JWT | Perfil del usuario |
| PATCH | `/perfil/actualizar/` | JWT | Actualizar nombre, apellido, teléfonos |
| POST | `/perfil/avatar/` | JWT | Multipart: `avatar` (archivo) |
| GET | `/sesiones/` | JWT | Listar sesiones |
| POST | `/sesiones/<id>/revocar/` | JWT | Revocar sesión |
| GET | `/2fa/estado/` | JWT | `{ tiene_2fa }` |
| GET | `/2fa/setup/` | JWT | `{ secret, provisioning_uri }` |
| POST | `/2fa/activar/` | JWT | Body: `secret`, `codigo` |
| POST | `/2fa/desactivar/` | JWT | Body: `codigo` |
| POST | `/restablecer-password/solicitar/` | No | Body: `{ email }` |
| POST | `/restablecer-password/` | No | Body: `token`, `nueva_password`, `nueva_password_confirm` |

---

## 4. Estructura creada (resumen)

```
backend/django_app/
  core/
    models.py          # Rol, Usuario, Perfil, VerificacionEmail, VerificacionOTP, Sesion, TOTP2FA
    admin.py           # Admin para todos los modelos
    serializers.py     # DRF serializers
    views.py           # API views (registro, login, perfil, sesiones, 2FA)
    urls.py            # /api/auth/*
    services/
      auth_service.py  # Lógica: registro, verificación, tokens, 2FA
      profile_service.py
    jobs/
      email.py         # Envío de emails (verificación, OTP, restablecer)
    management/commands/
      seed_auth.py     # python manage.py seed_auth
frontend/
  src/
    api/auth.ts        # Cliente API
    contexts/AuthContext.tsx
    pages/             # Login, Register, VerifyEmail, VerifyOTP, Dashboard, Profile, etc.
```

---

## 5. Login rápido (usuario demo)

1. Backend: `python manage.py runserver 8000` y (opcional) `uvicorn main:app --reload --port 8001`.
2. Frontend: `npm run dev` en `frontend/`.
3. Ir a http://localhost:5173/ingresar.
4. Email: **demo@safelease.local**, contraseña: **password**.
