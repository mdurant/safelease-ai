# SafeLease AI — Negocio

Documento de módulos de negocio del producto.

---

## Índice

1. [Módulo de Identidad y Acceso](#1-módulo-de-identidad-y-acceso)
2. [Módulo de Onboarding de Publicación](#2-módulo-de-onboarding-de-publicación)
3. [Módulo de Gestión de Propiedades y Arriendos](#3-módulo-de-gestión-de-propiedades-y-arriendos)
4. [Módulo de Suscripciones y Monetización](#4-módulo-de-suscripciones-y-monetización)
5. [Módulo de Pagos](#5-módulo-de-pagos)
6. [Módulo de Publicación y Visibilidad](#6-módulo-de-publicación-y-visibilidad)
7. [Módulo Landing + Búsqueda Pública](#7-módulo-landing--búsqueda-pública)
8. [Módulo Análisis de Fraude (OSINT)](#8-módulo-análisis-de-fraude-osint)
9. [Módulo de Fuentes OSINT chilenas](#9-módulo-de-fuentes-osint-chilenas)
10. [Módulo de Notificaciones](#10-módulo-de-notificaciones)
11. [Módulo de Moderación y Trust & Safety](#11-módulo-de-moderación-y-trust--safety)
12. [Módulo de Observabilidad y Auditoría](#12-módulo-de-observabilidad-y-auditoría)
13. [Stack sugerido y nota de producto](#13-stack-sugerido-y-nota-de-producto)

---

## 1. Módulo de Identidad y Acceso (Registro / Login)

**Responsabilidad**

- Registro, login, recuperación de contraseña, verificación email/teléfono (step-up).
- **Roles:** owner (publica), viewer (navega), admin (moderación/operación).

**Submódulos**

| Submódulo | Descripción |
|-----------|-------------|
| Auth | JWT/OAuth2, refresh tokens, sesiones |
| Account Profile | Datos del publicador (KYC "lite" opcional) |
| Security/Abuse | Rate limiting, detección de bots (por IP/device), bloqueo temporal |

**Datos clave**

- `user_id`, `email_hash`, `phone_hash`, `verified_email`, `verified_phone`, `created_at`
- `device_id`, `ip_first_seen_at`, contadores de intentos

---

## 2. Módulo de Onboarding de Publicación (Workflow "Publicar Arriendo")

Este módulo implementa el estado del flujo, guardando "borradores" y validaciones.

**Estados sugeridos**

- `DRAFT_CREATED`
- `DETAILS_COMPLETED`
- `PAYMENT_METHOD_ADDED`
- `VALIDATED`
- `SUBSCRIPTION_SELECTED`
- `PUBLISHED`

**Submódulos**

| Submódulo | Descripción |
|-----------|-------------|
| Draft Manager | Guardar/retomar borrador, versionado |
| Validation Engine (publicación) | Reglas de calidad (campos obligatorios, duplicados, fotos, contacto) |
| Media Manager | Fotos, thumbnails, hashing para detectar reuso |

---

## 3. Módulo de Gestión de Propiedades y Arriendos (Listing Service)

**Responsabilidad**

- CRUD de propiedades/arriendos, disponibilidad, precios, ubicación, reglas.
- **Versionado:** cada cambio crea "revisión".

**Submódulos**

| Submódulo | Descripción |
|-----------|-------------|
| Property Catalog | Entidad Propiedad |
| Rental Offer | La oferta (precio por noche/semana, condiciones, políticas) |
| Content Moderation (básico) | Filtros de lenguaje, detección de spam |

**Datos clave**

- `listing_id`, `owner_id`, `title`, `description`, `address_approx` (no exponer exacto si no corresponde)
- `contact_email`, `contact_phone`, `photos[]`, `price`, `currency`, `terms`

---

## 4. Módulo de Suscripciones y Monetización (Subscription & Plans)

**Responsabilidad**

- Planes (gratis / destacada / premium), límites, vigencia, facturación.
- "Pagar para publicar" o "pagar para destacar" (según negocio).

**Submódulos**

| Submódulo | Descripción |
|-----------|-------------|
| Plan Catalog | Planes y beneficios |
| Entitlements | Qué puede hacer cada plan (n publicaciones, highlight, etc.) |
| Billing History | Comprobantes, estados |

---

## 5. Módulo de Pagos (Payment Service)

**Responsabilidad**

- Integrar proveedor (ej. Stripe/MercadoPago/Transbank vía gateway).
- Cobro de suscripción y conciliación.

**Submódulos**

| Submódulo | Descripción |
|-----------|-------------|
| Payment Intent | Crear intención de pago |
| Webhook Handler | Confirmar pago y actualizar estado |
| Fraud-lite en pagos (opcional) | Controles básicos para evitar abuso de tarjetas |

---

## 6. Módulo de Publicación y Visibilidad (Publishing & Indexing)

**Responsabilidad**

- Pasar el listing a público y garantizar buscabilidad.
- Indexar en motor de búsqueda interno (Postgres FTS / OpenSearch).

**Submódulos**

| Submódulo | Descripción |
|-----------|-------------|
| Publish Controller | Solo publica si el workflow está completo y pagado |
| Search Indexer | Indexa título/ubicación/precio |
| Public URL Manager | Slug, canonical, SEO |

---

## 7. Módulo Landing + Búsqueda Pública (Discovery)

**Responsabilidad**

Landing público, filtros, resultados, ficha de propiedad.

**Submódulos**

| Submódulo | Descripción |
|-----------|-------------|
| Search & Filters | Destino, fechas, precio, tipo, rating (si existe) |
| Listing Details Page | Fotos, condiciones, contacto (según políticas) |
| CTA "Análisis de Fraude" | Inicia el escaneo OSINT del anuncio |

---

## 8. Módulo "Análisis de Fraude" (OSINT Fraud Analysis)

Este módulo se ejecuta cuando un usuario, viendo la propiedad publicada, presiona "Análisis de Fraude".

### 8.1 Orquestador de análisis (Fraud Orchestrator)

**Responsabilidad**

Crear un "job" de análisis, disparar conectores, agregar resultados y emitir progreso en tiempo real.

**Componentes**

- **Job Manager:** `analysis_job_id`, estado (`QUEUED` / `RUNNING` / `DONE` / `FAILED`)
- **Scheduler/Queue:** Celery/RQ + Redis (o Kafka)
- **Progress Events:** WebSocket o SSE para UI "en vivo"

**Salida**

- `risk_level`: LOW / MEDIUM / HIGH
- `risk_score`: 0..100
- `evidence[]`: hallazgos con links + por qué suben/bajan riesgo
- `recommendations[]`: "qué verificar antes de transferir/arrendar"

### 8.2 Conectores de Fuentes (Source Connectors)

**Responsabilidad**

Conectar con N fuentes públicas (configurable). Cada fuente implementa una interfaz común.

**Interfaz sugerida**

```text
search(listing_context) -> findings[]
fetch(url) -> page_data
extract(page_data) -> signals
confidence y source_reliability
```

**Importante**

Para Facebook/Instagram/Google/Booking/Airbnb, ideal usar APIs oficiales o enlaces aportados por el usuario; el scraping directo puede chocar con ToS. El diseño debe soportar ambos (API / scraping / "user-provided link").

### 8.3 Configuración de Fuentes (Dynamic Sources Registry)

**Responsabilidad**

Permitir que "inicialmente fijas" y luego administrables:

- activar/desactivar fuentes
- prioridad y timeout
- reglas por fuente
- credenciales (si API)
- rate limits

**Entidad**

```text
SourceDefinition { id, name, type(api|scrape|rss), base_url, enabled, weight, parsing_rules }
```

### 8.4 Adquisición y Scraping (Crawling Layer)

**Responsabilidad**

- Descargar contenido web (cuando aplique) de forma segura.
- Respetar robots/ToS cuando corresponda.
- Evitar bloqueos con rate limiting.

**Herramientas típicas en Python**

- `httpx` / `requests`, `BeautifulSoup` / `lxml`
- Playwright para páginas dinámicas
- Cache de respuestas (Redis) por URL/TTL

### 8.5 Extracción y Normalización (Extraction / Normalization)

**Responsabilidad**

Convertir HTML/texto en señales estructuradas.

**Señales típicas**

- Emails y teléfonos presentes (y cómo aparecen)
- Patrones de urgencia ("paga hoy", "última oportunidad")
- Condiciones sospechosas ("solo transferencia", "sin contrato", etc.)
- Reutilización de fotos/textos (mismo contenido en otros sitios)
- Dominio/correos raros, inconsistencias geográficas
- Fechas: anuncio nuevo con reviews antiguas (inconsistencia)

### 8.6 Intel de Contacto (Phone/Email Intelligence)

**Responsabilidad**

Validación y reputación de contacto.

**Ejemplos**

- Normalización de teléfono (+56…)
- Señales: teléfono reutilizado en múltiples anuncios con destinos distintos
- Señales regulatorias/spam: en Chile prefijos 600/809 (útil como señal contextual, aunque no prueba fraude)

**Nota legal/ética**

Si se hace "enriquecimiento" con rutificadores o fuentes de datos personales, diseñar con cumplimiento de privacidad (Ley 19.628), minimización y trazabilidad del uso.

### 8.7 Detección de Contenido Reutilizado (Text/Image Similarity)

**Responsabilidad**

Detectar si fotos y descripciones parecen robadas o duplicadas.

- **Imágenes:** hash perceptual (pHash/aHash)
- **Texto:** similitud semántica (embeddings) contra:
  - otras publicaciones dentro de la plataforma
  - fuentes externas consultadas en ese job

### 8.8 Correlación Multi-fuente (Evidence Fusion)

**Responsabilidad**

Unificar hallazgos de múltiples fuentes en un "grafo":

```text
listing ↔ phone ↔ email ↔ images ↔ external_posts ↔ domain
```

**Salida**

- evidencia deduplicada (no repetir lo mismo de 5 fuentes)
- explicación legible para el usuario final

### 8.9 Scoring & Policy (Risk Engine)

**Responsabilidad**

Convertir señales → nivel de riesgo (bajo/medio/alto) y justificación.

**Inputs**

- conteo de matches en fuentes
- severidad por patrón (transferencia adelantada, urgencia, fotos robadas, etc.)
- "bad indicators" (teléfono/email muy repetidos, inconsistencias)
- "good indicators" (presencia consistente en múltiples plataformas confiables)

**Outputs**

- `risk_level`: LOW | MEDIUM | HIGH
- `risk_score`: 0..100
- `why`: top razones

### 8.10 UI Tiempo Real (Realtime Experience)

**Responsabilidad**

Mostrar al usuario "escaneando fuentes…" con progreso real.

**Implementación típica**

- **Backend** emite eventos: `SOURCE_STARTED`, `SOURCE_DONE`, `MATCH_FOUND`, `SCORING_UPDATED`, `DONE`
- **Frontend** escucha por WebSocket/SSE y renderiza: lista de fuentes (check/ok/fail), hallazgos parciales, score que se actualiza

---

## 9. Módulo de Fuentes OSINT chilenas (configurables)

Fuentes de referencia y señales sugeridas:

| Fuente | Uso |
|--------|-----|
| **SERNAC / ODECU** | Recomendaciones y patrones comunes; motor de recomendaciones y patrones típicos de estafa (no tanto match directo) |
| **SUBTEL** | Señales asociadas a llamadas spam / identificación 600/809; reglas de "contacto sospechoso" |
| **OSINT Chile** | Directorio/plataforma OSINT; fuente "meta" o para enriquecer listados de verificación |
| **Grupos/denuncias en redes** (Facebook Groups, etc.) | Grupos donde se reportan estafas de arriendos. Preferir link aportado por usuario o API cuando sea posible (ToS) |
| **Prensa local** | Pattern library: catálogo de modus operandi actualizado (temporada de estafas de arriendos) |

---

## 10. Módulo de Notificaciones (Email / Push / WhatsApp opcional)

**Responsabilidad**

Enviar resultados o alertas:

- al usuario que pidió análisis ("tu informe está listo")
- al dueño del anuncio (opcional: "tu publicación fue marcada con señales X")
- a admins (picos de sospecha, abuso)

**Plantillas**

"Informe antifraude" con: riesgo + evidencia + recomendaciones.  
**Disclaimer:** "no es veredicto; decisión del usuario"

---

## 11. Módulo de Moderación y Trust & Safety (Administración)

**Responsabilidad**

- Revisión de publicaciones reportadas.
- Acciones: ocultar temporalmente, solicitar verificación, ban, etc.
- Lista de bloqueo/allow.

**Importante**

Separar **"riesgo OSINT"** (orientado al usuario) de **"acción de moderación"** (política interna).

---

## 12. Módulo de Observabilidad y Auditoría (Operación)

**Responsabilidad**

- Logs estructurados, métricas, trazas.
- **Auditoría de cada análisis:** qué fuentes se consultaron, qué URLs se visitaron, qué señales se extrajeron, por qué se llegó a LOW/MEDIUM/HIGH.
- **Control de costos:** scraping es caro; cache y límites.

---

## 13. Stack sugerido y nota de producto

### Stack sugerido (Python)

| Capa | Tecnología |
|------|------------|
| Backend | FastAPI + Pydantic |
| DB | Postgres (usuarios, listings, jobs, evidencias) |
| Cache/cola | Redis + Celery/RQ |
| Scraping | httpx + BeautifulSoup; Playwright para dinámicos |
| Tiempo real | WebSocket/SSE en FastAPI |
| Similitud | imagehash + PIL; embeddings (sentence-transformers o servicio externo) |
| Notificaciones | SMTP / SendGrid / etc. |

### Nota clave de producto ("wow")

El **Análisis de Fraude** debe entregar:

1. **Nivel de riesgo** (bajo/medio/alto)
2. **Evidencia navegable** (links y coincidencias)
3. **Explicación humana** (3–6 razones principales)
4. **Checklist accionable** ("verifica X antes de transferir")
5. **Transparencia:** "esto es OSINT, puede haber falsos positivos/negativos"
