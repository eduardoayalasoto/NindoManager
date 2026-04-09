# 🚀 PROMPT DE DESARROLLO - NINDO TASK MANAGEMENT SYSTEM
## Aplicación Django + PostgreSQL + Vue.js

---

## 📋 DESCRIPCIÓN DEL PROYECTO

Desarrollar una **aplicación web de administración de tareas recurrentes y registro de actividades** para NINDO Combat Center, que permita gestionar operaciones en múltiples sucursales con diferentes roles y permisos.

### Características principales:
- ✅ Gestión de usuarios con roles y permisos
- ✅ Sistema de tareas recurrentes (Lunes a Sábado)
- ✅ Módulos por sucursal (Lomas Verdes, Condesa)
- ✅ Registro de actividades y auditoría
- ✅ Dashboard interactivo con Vue.js
- ✅ Notificaciones por whatsapp por perfil
- ✅ Deployment en Railway con PostgreSQL

---

## 🛠️ STACK TECNOLÓGICO

### Backend
- **Framework**: Django 4.2+ (última versión LTS)
- **Base de datos**: PostgreSQL (en volumen estático de Railway)
- **Vistas**: Django Template Language (DTL)
- **Autenticación**: Django Auth + Tokens
- **Tareas en background**: Celery + Redis (para emails y tareas recurrentes)
- **Emails**: Django-anymail + SendGrid/SMTP
- **ORM**: Django ORM nativo
- **Validación**: Django Forms + DRF Serializers (para validación)
- **Logging y Auditoría**: Audit logging personalizado

### Frontend
- **Framework**: Vue.js 3 (opciones: Vite o Webpack)
- **Estado**: Pinia (state management)
- **HTTP**: Axios
- **UI**: TailwindCSS + Headless UI
- **Componentes**: Vue Components reutilizables
- **Calendarios**: Vue-Calendar o similar
- **Gráficos**: Chart.js o similar para reportes

### DevOps & Deployment
- **Hosting**: Railway.app
- **Base de datos**: PostgreSQL en volumen estático Railway
- **Caché**: Redis (en Railway o local)
- **Tasks**: Celery Beat para tareas recurrentes
- **Servidor web**: Gunicorn + Whitenoise
- **Reverse Proxy**: Nginx (si es necesario)

### Herramientas de desarrollo
- **Gestor de versiones**: Python 3.11+
- **Ambiente virtual**: venv
- **Dependencias**: pip + requirements.txt
- **Control de versión**: Git
- **Linting**: Black, Flake8
- **Testing**: pytest-django

---

## 📊 ARQUITECTURA BASE DE DATOS

### Modelos principales:

#### 1. **User (Extensión de Django User)**
```
- id (PK)
- username (unique)
- email (unique)
- first_name
- last_name
- is_active
- is_staff
- created_at
- updated_at
- avatar (ImageField, opcional)
```

#### 2. **Role**
```
- id (PK)
- name (string, unique) → "Jefa de Operaciones", "Gerente General", "Entrenador", "Admin"
- description (text)
- permissions (ManyToMany a Permission)
- created_at
- updated_at
```

#### 3. **UserRole**
```
- id (PK)
- user (FK a User)
- role (FK a Role)
- branch (FK a Branch)
- assigned_at
- assigned_by (FK a User)
```

#### 4. **Branch (Sucursal)**
```
- id (PK)
- name (string) → "Lomas Verdes", "Condesa"
- code (string, unique) → "LV", "CD"
- address (text)
- phone (string)
- email (string)
- is_active (boolean)
- created_at
- updated_at
```

#### 5. **TaskModule (Módulo de tareas)**
```
- id (PK)
- name (string) → "Limpieza", "Operaciones", "Administrativo", "Reportes"
- description (text)
- icon (string, opcional)
- order (integer)
- created_at
- updated_at
```

#### 6. **Task (Tarea base)**
```
- id (PK)
- title (string)
- description (text)
- module (FK a TaskModule)
- branch (FK a Branch)
- created_by (FK a User)
- assigned_to (FK a User, nullable)
- priority (choice) → "Alta", "Media", "Baja"
- estimated_duration (integer, minutos)
- is_recurring (boolean)
- recurring_pattern (JSON) → {"days": ["Monday", "Tuesday", ...]}
- status (choice) → "Pendiente", "En progreso", "Completada", "Cancelada"
- due_date (datetime)
- completed_at (datetime, nullable)
- created_at
- updated_at
```

#### 7. **TaskInstance (Instancia de tarea recurrente)**
```
- id (PK)
- task (FK a Task)
- branch (FK a Branch)
- assigned_to (FK a User)
- due_date (datetime)
- status (choice) → "Pendiente", "En progreso", "Completada", "Retrasada"
- started_at (datetime, nullable)
- completed_at (datetime, nullable)
- notes (text, nullable)
- created_at
- updated_at
```

#### 8. **TaskChecklist (Checklist de tareas)**
```
- id (PK)
- task (FK a Task)
- item (string)
- order (integer)
- created_at
- updated_at
```

#### 9. **TaskChecklistItem (Ítems completados del checklist)**
```
- id (PK)
- checklist (FK a TaskChecklist)
- task_instance (FK a TaskInstance)
- is_completed (boolean)
- completed_by (FK a User, nullable)
- completed_at (datetime, nullable)
```

#### 10. **Activity (Registro de actividades)**
```
- id (PK)
- user (FK a User)
- branch (FK a Branch)
- action (string) → "Crear", "Actualizar", "Completar", "Eliminar", "Asignar"
- content_type (string) → "Task", "User", "Role", etc.
- object_id (integer)
- description (text)
- old_values (JSON, nullable)
- new_values (JSON, nullable)
- ip_address (string, nullable)
- timestamp (datetime)
```

#### 11. **Notification**
```
- id (PK)
- user (FK a User)
- title (string)
- message (text)
- notification_type (choice) → "Task", "Alert", "System"
- related_task (FK a Task, nullable)
- is_read (boolean)
- created_at
- updated_at
```

#### 12. **EmailLog (Log de emails enviados)**
```
- id (PK)
- recipient (email)
- subject (string)
- body (text)
- status (choice) → "Pending", "Sent", "Failed"
- error_message (text, nullable)
- sent_at (datetime, nullable)
- created_at
```

---

## 🎯 FUNCIONALIDADES POR MÓDULO

### 1. **MÓDULO DE AUTENTICACIÓN Y USUARIOS**
- ✅ Login/Logout seguro
- ✅ Recuperación de contraseña por email
- ✅ Gestión de perfil de usuario
- ✅ Cambio de contraseña
- ✅ Vista de usuarios (solo para Admin)
- ✅ Asignación de roles por sucursal
- ✅ Desactivación de usuarios
- ✅ Historial de login (opcional)

### 2. **MÓDULO DE ROLES Y PERMISOS**
- ✅ CRUD de roles (solo Admin)
- ✅ Asignación de permisos a roles
- ✅ Validación de permisos en vistas
- ✅ Roles predefinidos:
  - **Superadmin**: Acceso total
  - **Jefa de Operaciones**: Manage tasks de su sucursal
  - **Gerente General**: Vista de todas las sucursales
  - **Entrenador**: Ver solo sus tareas asignadas

### 3. **MÓDULO DE SUCURSALES**
- ✅ CRUD de sucursales (solo Admin/Gerente General)
- ✅ Información de contacto
- ✅ Asignación de personal
- ✅ Estadísticas por sucursal

### 4. **MÓDULO DE TAREAS RECURRENTES**
- ✅ CRUD de tareas (Jefa de Ops, Admin)
- ✅ Crear tareas recurrentes (Lun-Sáb)
- ✅ Generación automática de instancias diarias via Celery
- ✅ Vista de tareas del día/semana
- ✅ Checklist por tarea
- ✅ Estados: Pendiente → En progreso → Completada

### 5. **MÓDULO DE ACTIVIDADES Y AUDITORÍA**
- ✅ Registro automático de todas las acciones (CRUD)
- ✅ Quién hizo qué, cuándo y dónde
- ✅ Registro de cambios (old_values, new_values)

### 6. **MÓDULO DE NOTIFICACIONES**
- ✅ Notificaciones in-app
- ✅ Emails automáticos (asignación, diario 7AM, resumen viernes 5PM)
- ✅ Notificaciones por WhatsApp por perfil

### 7. **MÓDULO DE DASHBOARD Y REPORTES**
- ✅ Vista general de tareas del día
- ✅ Estadísticas: Completadas, Pendientes, Retrasadas
- ✅ Gráfico de tendencias
- ✅ Calendario interactivo

---

## 🎨 DISEÑO Y COLORES (NINDO Brand)

- **Negro** (`#000000`): Fondos oscuros, tipografía principal
- **Blanco** (`#FFFFFF`): Fondos claros, tipografía sobre oscuro
- **Rojo Nindo** (`#CC0000`): Highlights, acciones importantes, CTAs
- Fondo principal siempre **blanco**
- Logo siempre sobre fondo blanco

---

## 🎯 OBJETIVOS POR FASE

### FASE 1: MVP (2-3 semanas) - ACTUAL
- Autenticación y roles
- CRUD de tareas básico
- Generación de instancias diarias
- Dashboard simple
- Notificaciones por WhatsApp por perfil

### FASE 2: Mejoras (2 semanas)
- Reportes
- Auditoría completa
- Calendario interactivo
- Notificaciones in-app
- UI mejorada

### FASE 3: Producción (1 semana)
- Deployment en Railway
- Testing extensivo
- Optimización de performance
- Documentación

---

## 🚀 DEPLOYMENT EN RAILWAY

### Variables de entorno necesarias:
```
DEBUG=False
SECRET_KEY=tu_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/nindo_db
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@nindocombat.com
WHATSAPP_API_TOKEN=tu_token
```

---

## 📦 DEPENDENCIAS PRINCIPALES

```
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
psycopg2-binary==2.9.9
celery==5.3.4
redis==5.0.1
django-anymail==10.2
Pillow==10.1.0
python-decouple==3.8
gunicorn==21.2.0
whitenoise==6.6.0
pytest-django==4.7.0
```

---

**Desarrollado para**: NINDO Combat Center
**Versión**: 1.0
**Stack**: Django 4.2 + PostgreSQL + Vue.js 3 + TailwindCSS
**Deployment**: Railway.app
