# NINDŌ Manager

Sistema de gestión operativa para NINDO Combat Center.

## Stack

- **Backend**: Django 4.2 + SQLite (dev) / PostgreSQL (prod opcional)
- **Frontend**: Django Templates + Tailwind CSS v4 + Alpine.js
- **Notificaciones**: WhatsApp (Meta API / Twilio / Console)
- **Tareas en background**: Celery + Redis (opcional en dev)
- **Deploy**: Railway.app

---


## UI moderno (Tailwind CSS v4)

Este proyecto compila estilos con **Tailwind CSS v4** desde `static/src/tailwind.css` hacia `static/css/app.css`.

```bash
npm install
npm run tailwind:build   # build minificado
npm run tailwind:watch   # desarrollo
```

Los componentes reutilizables viven en `templates/components/ui/`.

---

## Setup local (desarrollo)

**Requisitos:** Python 3.11+

```bash
# 1. Entorno virtual e instalación
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Variables de entorno
cp .env.example .env
# En desarrollo no necesitas cambiar nada — SQLite + console para emails y WhatsApp

# 3. Migraciones y datos iniciales
python manage.py migrate
python manage.py load_initial_data   # Crea sucursales, roles y 8 tareas de Recepción

# 4. Superusuario
python manage.py createsuperuser

# 5. Servidor
python manage.py runserver
```

Abre http://localhost:8000 e inicia sesión con tu superusuario.

---

## Setup Railway (producción con SQLite)

1. Crea un proyecto en Railway y conecta el repositorio.
2. Agrega un **Volume** en Railway y móntalo en `/mnt/data`.
3. Configura las variables de entorno en Railway:

```
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=genera-una-clave-larga-y-segura
ALLOWED_HOSTS=tu-dominio.railway.app
DATABASE_URL=sqlite:////mnt/data/db.sqlite3
WHATSAPP_PROVIDER=meta    # o twilio, o console para pruebas
WHATSAPP_API_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
```

El `startCommand` en `railway.toml` corre automáticamente migrate + load_initial_data.

---

## WhatsApp — Proveedores disponibles

Configura `WHATSAPP_PROVIDER` en tu `.env`:

| Valor | Descripción | Requiere |
|-------|-------------|----------|
| `console` | Imprime en terminal | Nada (para desarrollo) |
| `meta` | Meta Cloud API | Cuenta Meta Business + número verificado |
| `twilio` | Twilio WhatsApp | Cuenta Twilio + `pip install twilio` |

---

## Tareas iniciales cargadas (Recepción)

| # | Tarea | Días | Duración est. |
|---|-------|------|---------------|
| 1 | Responder redes sociales | Lun–Sáb | 30 min |
| 2 | Supervisión de limpieza | Lun–Sáb | 20 min |
| 3 | Inventario semanal | Lunes | 60 min |
| 4 | Caja diaria | Lun–Sáb | 45 min |
| 5 | Cobranza | Lun–Sáb | 45 min |
| 6 | Ventas | Lun–Sáb | 60 min |
| 7 | Seguimiento de leads | Lun–Sáb | 30 min |
| 8 | Seguimiento de clases muestra | Lun–Sáb | 30 min |

Todas las tareas tienen checklist de verificación integrado.

---

## Documentación del proyecto

Ver [docs/DEVELOPMENT_PROMPT.md](docs/DEVELOPMENT_PROMPT.md).
