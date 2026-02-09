# Módulos Técnicos — To-Be y Diagrama de Pantallas

Documento técnico To-Be que alinea el **diagrama de pantallas básicas/iniciales** del proyecto (Landing, Registro, Validación Email/OTP, Dashboard, Publicar Propiedad, Perfil, 2FA, Sesiones) con los módulos de negocio definidos en [Negocio.md](Negocio.md) y [ESTRATEGIA-NEGOCIO.md](ESTRATEGIA-NEGOCIO.md). Incluye procesos completos por módulo, orden de migraciones y seeders (español — Chile).

---

## Índice

1. [Diagrama de pantallas básicas/iniciales](#1-diagrama-de-pantallas-básicasiniciales)
2. [Módulo: Autenticación, Perfil, Avatar, Contraseña, 2FA, Sesiones](#2-módulo-autenticación-perfil-avatar-contraseña-2fa-sesiones)
3. [Módulo: Mis Publicaciones](#3-módulo-mis-publicaciones)
4. [Módulo: Editar un Alojamiento](#4-módulo-editar-un-alojamiento)
5. [Módulo: Mis Mensajes](#5-módulo-mis-mensajes)
6. [Módulo: Pack de Avisos (pago suscripción)](#6-módulo-pack-de-avisos-pago-suscripción)
7. [Módulo: Ayuda](#7-módulo-ayuda)
8. [Módulo: Motor Anti-Fraude OSINT](#8-módulo-motor-anti-fraude-osint)
9. [To-Be List: actividades, migraciones, seeders](#9-to-be-list-actividades-migraciones-seeders)

---

## 1. Diagrama de pantallas básicas/iniciales

Flujo derivado del documento “Your First Project” (pantallas iniciales):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LANDING PÚBLICA                                                             │
│ • Header: Logo | "Publicar Gratis" | "Ingresar"                             │
│ • Buscador: ¿A dónde quieres ir? | Llegada | Salida | Personas | Buscar     │
│ • Destinos populares (ej. Norte)                                            │
│ • Avisos destacados (cards: título, descripción, SUPER DESTACADO)           │
│ • Footer: Sobre IntegralTech | Ayuda y Soporte | Síguenos                   |
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ├── "Ingresar" ───────────────────────────────────────────────────────┐
        │                                                                     │
        └── "Publicar Gratis" / "Crear cuenta"                                │
                    │                                                         │
                    ▼                                                         │
┌─────────────────────────────────────────────────────────────────────────────┐
│ CREAR CUENTA                                                                │
│ • Nombre, Apellido, Teléfono, Email, Contraseña, Confirmar contraseña       │
│ • Aceptar términos y condiciones | Botón "Crear Cuenta"                     │
└─────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENVÍO MAIL VALIDACIÓN                                                       │
│ • Mensaje: "Te enviamos un mail a {{email}} para verificar y activar..."    │
│ • Link a ayuda: ayuda@integraltech.cl                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                    │ (usuario hace clic en link del mail)
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ VERIFICACIÓN EMAIL (landing post-clic)                                      │
│ • "Validaste tu correo electrónico" | "La cuenta {{email}} ya está lista"   │
│ • Mensaje: "Revisa tu bandeja, llegará código de 6 dígitos para validar"    │
└─────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ VALIDACIÓN OTP (6 dígitos)                                                  │
│ • Input 6 dígitos | "Ingresa los 6 dígitos para validar"                    │
│ • Resultado: "Validación correcta! Hola {{Usuario}}"                        │
└─────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ DASHBOARD (usuario autenticado)                                             │
│ • Nav: Dashboard | Mis Publicaciones | Mis Mensajes | Pack de Avisos | Ayuda│
│ • "Publicar un nuevo lugar" (CTA)                                           │
│ • Contenido según sección (ver módulos 3–7)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ├── Perfil / Tus Datos ──► Perfil │ Contraseña │ Modal 2FA │ Gestión 2FA │ Sesiones Activas
        ├── Publicar un nuevo lugar ──► Step 1: Datos + Alojamiento → Step 2: Ubicación → Step 3: Calendario
        └── (resto de módulos)
```

**Resumen de pantallas por módulo**

| Módulo | Pantallas clave |
|--------|------------------|
| Auth / Perfil | Landing, Crear cuenta, Envío mail, Verificación email, Validación OTP, Dashboard; Perfil, Contraseña, Modal 2FA, Gestión 2FA, Sesiones activas |
| Publicar / Editar alojamiento | Dashboard step 1 (Datos + Alojamiento), step 2 (Ubicación), step 3 (Calendario); listado Mis Publicaciones; edición por paso |
| Mis Mensajes | Vista lista + detalle (dentro del Dashboard) |
| Pack de Avisos | Selección de plan y pago (dentro del Dashboard) |
| Ayuda | Enlaces footer + sección Ayuda (Contacto, Soporte, Términos) |
| Motor Anti-Fraude | CTA en ficha de propiedad → flujo análisis en tiempo real (ver módulo 8) |

---

## 2. Módulo: Autenticación, Perfil, Avatar, Contraseña, 2FA, Sesiones

### 2.1 Proceso completo (To-Be)

| # | Actividad | Pantalla / API | Regla de negocio |
|---|-----------|----------------|-------------------|
| 1 | Registro | Crear cuenta | Validar email único, teléfono opcional; contraseña con política (longitud, complejidad). Hash de contraseña (bcrypt/argon2). |
| 2 | Envío verificación email | Post-registro | Token único con expiración (ej. 24 h); enviar mail con link `verificar-email?cr=<token>`. |
| 3 | Verificación email | Landing post-clic | Consumir token; marcar `verified_email=true`; opcionalmente disparar envío OTP 6 dígitos. |
| 4 | Validación OTP (6 dígitos) | Pantalla OTP | Código enviado por email (o SMS); TTL corto (ej. 10 min); tras éxito, marcar usuario como “completamente verificado” (step-up listo para publicar). |
| 5 | Login | Ingresar | JWT access + refresh; registrar device_id e IP; rate limiting por IP/email. |
| 6 | Recuperación contraseña | “Olvidé contraseña” | Token por email; pantalla nueva contraseña; invalidar sesiones si se exige. |
| 7 | Perfil (Tus Datos) | Dashboard > Perfil | Editar nombre, apellido, teléfono, teléfono alternativo; avatar = subida de imagen (Media Manager). |
| 8 | Cambio de contraseña | Dashboard > Contraseña | Requiere contraseña actual; nueva + confirmación; invalidar otros refresh tokens (opcional). |
| 9 | Habilitación 2FA | Modal 2FA / Gestión 2FA | TOTP (Google Authenticator, etc.); backup codes; flujo: activar → escanear QR → validar código → guardar. |
| 10 | Sesiones activas | Dashboard > Sesiones activas | Listar sesiones (device, IP, última actividad); “Cerrar otras sesiones” / “Cerrar esta”. |

### 2.2 Pantallas (referencia PDF)

- **Landing** → **Crear Cuenta** → **Envío Mail** → **Verificación Email** → **Validación OTP** → **Dashboard**.
- **Dashboard** → **Tus Datos (Perfil)** | **Contraseña** | **Modal 2FA** | **Gestión 2FA** | **Sesiones Activas**.

### 2.3 Tablas y dependencias (para migraciones)

- `core_rol` (id, nombre, codigo) — ej. owner, viewer, admin.
- `core_usuario` (id, email_hash, phone_hash, verified_email, verified_phone, created_at, rol_id, …).
- `core_perfil` (id, usuario_id, nombre, apellido, telefono, telefono_alternativo, avatar_url, …).
- `core_verificacion_email` (id, usuario_id, token, expira_en, usado_en).
- `core_verificacion_otp` (id, usuario_id, codigo_hash, expira_en, usado_en).
- `core_sesion` (id, usuario_id, device_id, ip, user_agent, refresh_token_hash, ultima_actividad, creado_en).
- `core_totp_2fa` (id, usuario_id, secret_cifrado, backup_codes_cifrado, activo, creado_en).

*(Las migraciones concretas se listan en la sección 9 en el orden correcto.)*

---

## 3. Módulo: Mis Publicaciones

### 3.1 Proceso completo (To-Be)

| # | Actividad | Pantalla / API | Regla de negocio |
|---|-----------|----------------|-------------------|
| 1 | Listar publicaciones del usuario | Dashboard > Mis Publicaciones | Solo listings con `owner_id = usuario actual`; estados: borrador, validado, publicado, pausado. |
| 2 | Crear borrador | “Publicar un nuevo lugar” | Crear listing en estado DRAFT_CREATED; flujo por pasos (Datos → Ubicación → Calendario). |
| 3 | Guardar / retomar borrador | Steps 1–3 | Draft Manager: versionado; validación por paso (Validation Engine). |
| 4 | Ver detalle / editar | Card → Editar | Redirige a “Editar un Alojamiento” (módulo 4). |
| 5 | Publicar (cuando aplica) | CTA Publicar | Solo si workflow completo y (según negocio) plan/suscripción activa; Publish Controller. |

### 3.2 Pantallas

- Listado de cards (título, miniatura, estado, fechas).
- Filtros/estado: Borrador, Publicado, Pausado.
- CTA “Publicar un nuevo lugar” inicia flujo de onboarding (steps 1–3).

### 3.3 Tablas

- `listados_listing`, `listados_listing_revision`, `listados_media` (dependen de `core_usuario` y de `geo_region`, `geo_comuna`; ver sección 9).

---

## 4. Módulo: Editar un Alojamiento

### 4.1 Proceso completo (To-Be)

Corresponde al flujo “Publicar un nuevo lugar” en 3 pasos (PDF):

| Paso | Contenido (pantalla) | Datos clave |
|------|----------------------|-------------|
| 1 | Tus Datos + Datos de Alojamiento | Nombre, email, teléfono; título, descripción, tipo propiedad, huéspedes min/max, habitaciones, baños, estacionamientos; modalidad arriendo; check-in/out; período mínimo; moneda (CLP); cargo aseo; servicios (Aire, Calefacción, TV, Wifi, Estacionamiento, Quincho, Mascotas, Otro). |
| 2 | Ubicación | Región, Comuna, Dirección, Código postal (Chile). |
| 3 | Calendario | Períodos de arriendo: fecha inicial/final, disponible/no disponible, precio por noche, moneda CLP. |

| # | Actividad | Regla de negocio |
|---|-----------|-------------------|
| 1 | Guardar paso 1 | Validation Engine: campos obligatorios; guardar/actualizar borrador (DRAFT_CREATED → DETAILS_COMPLETED). |
| 2 | Guardar paso 2 | Validar región/comuna (tabla comunas Chile); address_approx para no exponer exacto si aplica. |
| 3 | Guardar paso 3 | Guardar bloques de disponibilidad y precio; validar solapamientos. |
| 4 | Siguiente / Publicar | Transición de estados según ESTRATEGIA-NEGOCIO; al publicar: Publish Controller + Search Indexer. |

### 4.2 Tablas

- `listados_listing`, `listados_listing_revision`, `listados_disponibilidad`, `listados_servicio`, `listados_media`; `geo_region`, `geo_comuna`.

---

## 5. Módulo: Mis Mensajes

### 5.1 Proceso completo (To-Be)

| # | Actividad | Pantalla / API | Regla de negocio |
|---|-----------|----------------|-------------------|
| 1 | Listar conversaciones | Dashboard > Mis Mensajes | Por usuario: conversaciones donde participa; orden por última actividad. |
| 2 | Ver hilo / responder | Detalle conversación | Mensajes asociados a un listing; notificaciones (email/push) según módulo Notificaciones. |
| 3 | Iniciar contacto (desde ficha) | Ficha pública | Crear conversación listing + remitente + primer mensaje. |

### 5.2 Tablas

- `mensajes_conversacion`, `mensajes_mensaje` (usuario_id, listing_id, etc.).

---

## 6. Módulo: Pack de Avisos (pago suscripción)

### 6.1 Proceso completo (To-Be)

| # | Actividad | Pantalla / API | Regla de negocio |
|---|-----------|----------------|-------------------|
| 1 | Listar planes | Dashboard > Pack de Avisos | Plan Catalog: Gratis, Destacada, Premium; límites (n publicaciones, highlight). |
| 2 | Seleccionar plan | Checkout | Entitlements por plan; vigencia; mostrar precio en CLP. |
| 3 | Payment Intent | Pasarela | Crear intención (Stripe/MercadoPago/Transbank); redirigir a pago. |
| 4 | Webhook / confirmación | Backend | Actualizar estado suscripción; Billing History; activar beneficios. |
| 5 | Historial y comprobantes | Pack de Avisos / Billing | Listar comprobantes y estados (pagado, pendiente, fallido). |

### 6.2 Tablas

- `planes_plan`, `planes_entitlement`, `suscripciones_suscripcion`, `pagos_pago`, `pagos_comprobante`.

---

## 7. Módulo: Ayuda

### 7.1 Proceso completo (To-Be)

| # | Actividad | Pantalla / Contenido | Regla de negocio |
|---|-----------|----------------------|-------------------|
| 1 | Enlaces footer (Landing + Dashboard) | Sobre IntegralTech: Quiénes somos, Cómo funciona, Contacto, Blog, Trabaja con nosotros. | Estáticos o CMS. |
| 2 | Ayuda y Soporte | Contacto, Soporte Técnico, Términos y Condiciones. | Formulario contacto → ticket o email (ayuda@integraltech.cl). |
| 3 | Síguenos | Redes sociales. | Links externos. |

No requiere tablas nuevas críticas; opcional: `ayuda_ticket` o `ayuda_consulta` si se guardan consultas.

---

## 8. Módulo: Motor Anti-Fraude OSINT

### 8.1 Proceso completo (To-Be)

| # | Actividad | Pantalla / API | Regla de negocio |
|---|-----------|----------------|-------------------|
| 1 | CTA “Análisis de Fraude” | Ficha de propiedad (Discovery) | Solo para listings publicados; usuario (viewer o anónimo según diseño) inicia job. |
| 2 | Crear job | Backend | Fraud Orchestrator: analysis_job_id, estado QUEUED → RUNNING; cola (Celery/RQ). |
| 3 | Progreso en tiempo real | UI | WebSocket/SSE: SOURCE_STARTED, SOURCE_DONE, MATCH_FOUND, SCORING_UPDATED, DONE. |
| 4 | Resultado | Pantalla informe | risk_level (LOW/MEDIUM/HIGH), risk_score 0–100, evidence[], recommendations[]; disclaimer OSINT. |
| 5 | Notificación | Email (módulo Notificaciones) | “Tu informe está listo” con link al resultado. |

Conectores, fuentes, crawling, extracción, intel contacto, similitud texto/imagen, fusión y scoring según ESTRATEGIA-NEGOCIO (submódulos 8.2–8.9).

### 8.2 Tablas

- `fraude_job_analisis`, `fraude_fuente_definicion`, `fraude_hallazgo`, `fraude_evidencia`, `fraude_auditoria_job`.

---

## 9. To-Be List: actividades, migraciones, seeders

### 9.1 Orden lógico de migraciones (Django)

Las migraciones deben respetar dependencias entre apps y claves foráneas. Orden sugerido:

| Orden | App | Migración | Descripción |
|-------|-----|-----------|-------------|
| 1 | core | 0001_initial_rol | Tabla `core_rol` (id, nombre, codigo). |
| 2 | core | 0002_usuario | Tabla `core_usuario` (rol_id FK, email_hash, phone_hash, verified_email, verified_phone, created_at, etc.). |
| 3 | core | 0003_perfil | Tabla `core_perfil` (usuario_id FK, nombre, apellido, telefono, telefono_alternativo, avatar_url). |
| 4 | core | 0004_verificacion_email | Tabla `core_verificacion_email` (usuario_id, token, expira_en, usado_en). |
| 5 | core | 0005_verificacion_otp | Tabla `core_verificacion_otp` (usuario_id, codigo_hash, expira_en, usado_en). |
| 6 | core | 0006_sesion | Tabla `core_sesion` (usuario_id, device_id, ip, user_agent, refresh_token_hash, ultima_actividad, creado_en). |
| 7 | core | 0007_totp_2fa | Tabla `core_totp_2fa` (usuario_id, secret_cifrado, backup_codes_cifrado, activo, creado_en). |
| 8 | geo | 0001_region | Tabla `geo_region` (id, nombre, codigo) — regiones Chile. |
| 9 | geo | 0002_comuna | Tabla `geo_comuna` (id, region_id FK, nombre, codigo). |
| 10 | listados | 0001_listing_estado | Tabla `listados_estado_listing` (id, codigo, nombre) — DRAFT_CREATED, PUBLISHED, etc. |
| 11 | listados | 0002_listing | Tabla `listados_listing` (owner_id FK usuario, estado_id FK, titulo, descripcion, address_approx, contact_email, contact_phone, moneda, terms, slug, created_at, updated_at). |
| 12 | listados | 0003_listing_revision | Tabla `listados_listing_revision` (listing_id FK, version, payload JSON/snapshots, created_at). |
| 13 | listados | 0004_media | Tabla `listados_media` (listing_id FK, url, thumbnail_url, hash_archivo, orden, tipo). |
| 14 | listados | 0005_servicio | Tabla `listados_servicio` (id, codigo, nombre). |
| 15 | listados | 0006_listing_servicios | Tabla N:M listado–servicios (listing_id, servicio_id). |
| 16 | listados | 0007_disponibilidad | Tabla `listados_disponibilidad` (listing_id FK, fecha_inicio, fecha_fin, precio_noche, moneda, disponible). |
| 17 | planes | 0001_plan | Tabla `planes_plan` (id, nombre, codigo, precio, moneda, vigencia_dias, max_publicaciones, destacado). |
| 18 | planes | 0002_entitlement | Tabla `planes_entitlement` (plan_id FK, codigo_beneficio, valor). |
| 19 | suscripciones | 0001_suscripcion | Tabla `suscripciones_suscripcion` (usuario_id FK, plan_id FK, vigente_desde, vigente_hasta, estado). |
| 20 | pagos | 0001_pago | Tabla `pagos_pago` (suscripcion_id FK, monto, moneda, estado, gateway, id_externo, created_at). |
| 21 | pagos | 0002_comprobante | Tabla `pagos_comprobante` (pago_id FK, url_pdf, enviado_email). |
| 22 | mensajes | 0001_conversacion | Tabla `mensajes_conversacion` (listing_id FK, creador_id FK usuario, created_at). |
| 23 | mensajes | 0002_mensaje | Tabla `mensajes_mensaje` (conversacion_id FK, autor_id FK usuario, cuerpo, leido, created_at). |
| 24 | fraude | 0001_fuente_definicion | Tabla `fraude_fuente_definicion` (id, nombre, tipo, base_url, enabled, weight, parsing_rules JSON). |
| 25 | fraude | 0002_job_analisis | Tabla `fraude_job_analisis` (listing_id FK, usuario_solicitante_id FK nullable, estado, risk_level, risk_score, created_at, updated_at). |
| 26 | fraude | 0003_hallazgo_evidencia | Tablas `fraude_hallazgo`, `fraude_evidencia` (job_id FK, fuente_id FK, tipo, contenido, url, confidence, etc.). |
| 27 | fraude | 0004_auditoria_job | Tabla `fraude_auditoria_job` (job_id FK, fuente_id FK, url_consultada, señales_json, created_at). |
| 28 | notificaciones | 0001_log | Tabla opcional `notificaciones_envio` (usuario_id, tipo, canal, referencia_id, enviado_en). |

### 9.2 Lista de actividades To-Be (resumen ejecutable)

- [ ] **Core/Auth**: Implementar registro (Crear cuenta) + envío mail verificación + endpoint verificar-email + flujo OTP 6 dígitos.
- [ ] **Core/Auth**: Login JWT (access + refresh), rate limiting, registro de sesión (device_id, IP).
- [ ] **Core**: Recuperación de contraseña (token por email + pantalla nueva contraseña).
- [ ] **Core**: Perfil (CRUD Tus Datos) + subida avatar (Media Manager o storage S3/local).
- [ ] **Core**: Cambio de contraseña (contraseña actual + nueva) + opción invalidar otras sesiones.
- [ ] **Core**: 2FA: activar/desactivar TOTP, backup codes, pantalla Modal 2FA y Gestión 2FA.
- [ ] **Core**: Sesiones activas: listar y cerrar sesión(es).
- [ ] **Geo**: Seed regiones y comunas Chile (orden: regiones primero, luego comunas).
- [ ] **Listados**: CRUD borrador listing (pasos 1–3); validación por paso; versionado revisiones.
- [ ] **Listados**: Mis Publicaciones: listado por usuario, filtros estado; CTA Publicar.
- [ ] **Listados**: Editar alojamiento: mismos 3 pasos con datos precargados; Publish Controller al publicar.
- [ ] **Listados**: Media Manager: fotos, thumbnails, hashing; integración con listing.
- [ ] **Planes**: Seed planes (Gratis, Destacada, Premium) y entitlements.
- [ ] **Suscripciones/Pagos**: Payment Intent + Webhook; Billing History y comprobantes.
- [ ] **Mensajes**: Conversaciones por listing; listado Mis Mensajes; envío y lectura.
- [ ] **Ayuda**: Páginas estáticas y formulario contacto (y opcional tabla tickets).
- [ ] **Fraude**: Orquestador job + cola; conectores y Dynamic Sources Registry; WebSocket/SSE progreso.
- [ ] **Fraude**: UI resultado: risk_level, risk_score, evidence, recommendations, disclaimer.
- [ ] **Notificaciones**: Plantilla “Informe listo” y envío post-job.

### 9.3 Seeders (español — Chile)

Los seeders deben ejecutarse **después** de las migraciones que crean las tablas. Orden sugerido:

#### 9.3.1 Roles (core)

| codigo | nombre |
|--------|--------|
| owner | Publicador |
| viewer | Navegante |
| admin | Administrador |

#### 9.3.2 Regiones Chile (geo)

| codigo | nombre |
|--------|--------|
| 01 | Tarapacá |
| 02 | Antofagasta |
| 03 | Atacama |
| 04 | Coquimbo |
| 05 | Valparaíso |
| 06 | O'Higgins |
| 07 | Maule |
| 08 | Biobío |
| 09 | Araucanía |
| 10 | Los Lagos |
| 11 | Aysén |
| 12 | Magallanes |
| 13 | Metropolitana |
| 14 | Los Ríos |
| 15 | Arica y Parinacota |
| 16 | Ñuble |

#### 9.3.3 Comunas Chile (geo) — muestra (Metropolitana y otras)

Ejemplos para seed inicial (comunas dependen de región):

| region_codigo | codigo | nombre |
|---------------|--------|--------|
| 13 | 13101 | Santiago |
| 13 | 13102 | Cerrillos |
| 13 | 13103 | Cerro Navia |
| 13 | 13104 | Conchalí |
| 13 | 13105 | El Bosque |
| 13 | 13106 | Estación Central |
| 13 | 13107 | Huechuraba |
| 13 | 13108 | Independencia |
| 13 | 13109 | La Cisterna |
| 13 | 13110 | La Florida |
| 13 | 13111 | La Granja |
| 13 | 13112 | La Pintana |
| 13 | 13113 | La Reina |
| 13 | 13114 | Las Condes |
| 13 | 13115 | Lo Barnechea |
| 13 | 13116 | Lo Espejo |
| 13 | 13117 | Lo Prado |
| 13 | 13118 | Macul |
| 13 | 13119 | Maipú |
| 13 | 13120 | Ñuñoa |
| 13 | 13121 | Pedro Aguirre Cerda |
| 13 | 13122 | Peñalolén |
| 13 | 13123 | Providencia |
| 13 | 13124 | Pudahuel |
| 13 | 13125 | Quilicura |
| 13 | 13126 | Quinta Normal |
| 13 | 13127 | Recoleta |
| 13 | 13128 | Renca |
| 13 | 13129 | San Joaquín |
| 13 | 13130 | San Miguel |
| 09 | 09101 | Temuco |
| 09 | 09102 | Carahue |
| 05 | 05101 | Valparaíso |
| 05 | 05102 | Viña del Mar |

*(En producción se cargan todas las comunas oficiales; aquí solo referencia para formato.)*

#### 9.3.4 Estado listing (listados)

| codigo | nombre |
|--------|--------|
| DRAFT_CREATED | Borrador creado |
| DETAILS_COMPLETED | Detalles completados |
| PAYMENT_METHOD_ADDED | Método de pago agregado |
| VALIDATED | Validado |
| SUBSCRIPTION_SELECTED | Suscripción seleccionada |
| PUBLISHED | Publicado |
| PAUSED | Pausado |

#### 9.3.5 Servicios incluidos (listados, se pueden agregar más)

| codigo | nombre |
|--------|--------|
| AIRE_ACONDICIONADO | Aire Acondicionado |
| CALEFACCION | Calefacción |
| TELEVISION | Televisión |
| WIFI | Wifi |
| ESTACIONAMIENTO | Estacionamiento |
| QUINCHO_PARRILLA | Quincho/Parrilla |
| ACEPTA_MASCOTAS | Acepta Mascotas |
| OTRO | Otro |

#### 9.3.6 Planes (planes)

| codigo | nombre | precio | moneda | vigencia_dias | max_publicaciones | destacado |
|--------|--------|--------|--------|------------------|-------------------|-----------|
| GRATIS | Gratis | 0 | CLP | 365 | 1 | false |
| DESTACADA | Destacada | 19990 | CLP | 30 | 5 | true |
| PREMIUM | Premium | 39990 | CLP | 30 | 20 | true |

#### 9.3.7 Entitlements por plan (planes)

| plan_codigo | codigo_beneficio | valor |
|-------------|------------------|-------|
| GRATIS | max_publicaciones | 1 |
| GRATIS | destacado | 0 |
| DESTACADA | max_publicaciones | 5 |
| DESTACADA | destacado | 1 |
| PREMIUM | max_publicaciones | 20 |
| PREMIUM | destacado | 1 |

#### 9.3.8 Fuentes OSINT iniciales (fraude) — configurables

| nombre | tipo | enabled | weight |
|--------|------|--------|--------|
| SERNAC recomendaciones | api | true | 0.8 |
| ODECU patrones | api | true | 0.8 |
| SUBTEL señales 600 809 | api | true | 0.5 |
| OSINT Chile directorio | scrape | true | 0.6 |
| Prensa local pattern library | rss | true | 0.5 |

*(base_url y parsing_rules se definen en migración o en seeder según implementación.)*

### 9.4 Orden de ejecución recomendado

1. Aplicar todas las migraciones en el orden de la tabla 9.1.
2. Ejecutar seeders en este orden: **Roles** → **Regiones** → **Comunas** → **Estado listing** → **Servicios** → **Planes** → **Entitlements** → **Fuentes OSINT** (opcional usuario demo y suscripción de prueba).
3. Verificar integridad referencial (FKs) antes de seeders que dependan de tablas ya sembradas.

---

## Referencias

- [Negocio.md](Negocio.md) — Definición de módulos de negocio.
- [ESTRATEGIA-NEGOCIO.md](ESTRATEGIA-NEGOCIO.md) — Estrategia y submódulos.
- Diagrama de pantallas: documento “Your First Project (1).pdf” (Landing, Crear cuenta, Validación email/OTP, Dashboard, Publicar propiedad por pasos, Perfil, 2FA, Sesiones).
