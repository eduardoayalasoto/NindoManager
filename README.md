# NINDŌ Manager

Sistema de gestión operativa para NINDO Combat Center.

## Stack

- **Backend**: Django 4.2 + PostgreSQL
- **Frontend**: Django Templates + TailwindCSS + Alpine.js
- **Tasks**: Celery + Redis
- **Deploy**: Railway.app

## Setup local

```bash
# 1. Clonar e instalar dependencias
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Base de datos
createdb nindo_db
python manage.py migrate

# 4. Superusuario
python manage.py createsuperuser

# 5. Iniciar servidor
python manage.py runserver

# 6. (Opcional) Celery worker
celery -A config worker -l info
celery -A config beat -l info
```

## Variables de entorno requeridas

Ver `.env.example` para la lista completa.

## Documentación del proyecto

Ver [docs/DEVELOPMENT_PROMPT.md](docs/DEVELOPMENT_PROMPT.md) para el prompt completo de desarrollo y arquitectura.
