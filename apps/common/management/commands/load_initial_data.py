"""
Management command to load initial catalog data for Nindo Manager.

Usage:
    python manage.py load_initial_data
    python manage.py load_initial_data --reset   # clears and reloads everything

Creates:
  - Branches: Lomas Verdes, Condesa
  - Roles: Superadmin, Gerente General, Jefa de Operaciones, Recepción, Entrenador
  - Task Modules: Recepción, Limpieza, Operaciones, Administrativo
  - Tasks: 8 recurring tasks for Recepción (all Mon–Sat by default)
"""
from django.core.management.base import BaseCommand
from django.db import transaction


BRANCHES = [
    {"name": "Lomas Verdes", "code": "LV", "is_active": True},
    {"name": "Condesa", "code": "CD", "is_active": True},
]

ROLES = [
    {
        "name": "Superadmin",
        "description": "Acceso total al sistema.",
        "can_manage_users": True,
        "can_manage_branches": True,
        "can_manage_tasks": True,
        "can_view_all_branches": True,
        "can_view_reports": True,
        "can_view_activities": True,
    },
    {
        "name": "Gerente General",
        "description": "Visibilidad de todas las sucursales. No modifica configuración del sistema.",
        "can_manage_users": False,
        "can_manage_branches": False,
        "can_manage_tasks": True,
        "can_view_all_branches": True,
        "can_view_reports": True,
        "can_view_activities": True,
    },
    {
        "name": "Jefa de Operaciones",
        "description": "Gestiona tareas y personal de su sucursal.",
        "can_manage_users": False,
        "can_manage_branches": False,
        "can_manage_tasks": True,
        "can_view_all_branches": False,
        "can_view_reports": True,
        "can_view_activities": True,
    },
    {
        "name": "Recepción",
        "description": "Ejecuta tareas diarias de recepción, ventas y seguimiento.",
        "can_manage_users": False,
        "can_manage_branches": False,
        "can_manage_tasks": False,
        "can_view_all_branches": False,
        "can_view_reports": False,
        "can_view_activities": False,
    },
    {
        "name": "Entrenador",
        "description": "Ve únicamente las tareas que le son asignadas.",
        "can_manage_users": False,
        "can_manage_branches": False,
        "can_manage_tasks": False,
        "can_view_all_branches": False,
        "can_view_reports": False,
        "can_view_activities": False,
    },
]

# Mon–Sat recurring pattern (default for most tasks)
MON_SAT = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
MONDAY_ONLY = ["Monday"]

TASK_MODULES = [
    {"name": "Recepción", "icon": "desk", "order": 1, "description": "Tareas del área de recepción y atención al cliente."},
    {"name": "Limpieza", "icon": "broom", "order": 2, "description": "Supervisión y ejecución de protocolos de limpieza."},
    {"name": "Operaciones", "icon": "gear", "order": 3, "description": "Tareas operativas generales de la sucursal."},
    {"name": "Administrativo", "icon": "folder", "order": 4, "description": "Tareas administrativas, reportes y documentación."},
]

# Tasks from the director — all assigned to module "Recepción"
# Each entry: (title, description, priority, days, estimated_duration_min, checklist_items)
RECEPTION_TASKS = [
    (
        "Responder redes sociales",
        "Revisar y responder mensajes en Instagram, Facebook y WhatsApp del gimnasio. "
        "Mantener tiempo de respuesta menor a 1 hora.",
        "alta",
        MON_SAT,
        30,
        [
            "Revisar mensajes de Instagram",
            "Revisar mensajes de Facebook",
            "Revisar WhatsApp Business",
            "Responder consultas pendientes",
            "Registrar leads nuevos en el sistema",
        ],
    ),
    (
        "Supervisión de limpieza",
        "Verificar que las áreas de entrenamiento, vestidores y recepción estén limpias "
        "y en orden. Reportar cualquier incidencia.",
        "alta",
        MON_SAT,
        20,
        [
            "Revisar área de entrenamiento principal",
            "Revisar vestidores damas",
            "Revisar vestidores caballeros",
            "Revisar recepción y área de espera",
            "Revisar baños",
            "Reportar incidencias si existen",
        ],
    ),
    (
        "Inventario semanal",
        "Realizar conteo de inventario: equipos de entrenamiento, artículos de limpieza, "
        "papelería y merchandising. Reportar faltantes.",
        "media",
        MONDAY_ONLY,
        60,
        [
            "Contar equipos de entrenamiento",
            "Contar artículos de limpieza",
            "Contar papelería",
            "Contar merchandise (playeras, guantes, etc.)",
            "Actualizar hoja de inventario",
            "Reportar faltantes a Jefa de Operaciones",
        ],
    ),
    (
        "Caja diaria",
        "Realizar apertura y cierre de caja. Registrar todos los ingresos del día, "
        "cuadrar caja y entregar reporte al final del turno.",
        "alta",
        MON_SAT,
        45,
        [
            "Apertura de caja (contar efectivo inicial)",
            "Registrar todos los cobros del día",
            "Registrar cobros en terminal/transferencias",
            "Cierre de caja (cuadre)",
            "Capturar reporte diario",
            "Entregar reporte a Jefa de Operaciones",
        ],
    ),
    (
        "Cobranza",
        "Gestionar cobros pendientes de mensualidades vencidas. Contactar alumnos con "
        "adeudos y registrar acuerdos de pago.",
        "alta",
        MON_SAT,
        45,
        [
            "Revisar lista de alumnos con adeudo",
            "Contactar alumnos (WhatsApp/llamada)",
            "Registrar respuestas y acuerdos",
            "Actualizar estatus de cobranza",
            "Reportar casos sin respuesta",
        ],
    ),
    (
        "Ventas",
        "Atender prospectos presenciales y online. Presentar planes de membresía, "
        "procesar inscripciones y entregar materiales de bienvenida.",
        "alta",
        MON_SAT,
        60,
        [
            "Atender prospectos en recepción",
            "Presentar planes y precios",
            "Procesar inscripciones nuevas",
            "Registrar venta en el sistema",
            "Entregar kit de bienvenida",
            "Confirmar acceso al alumno",
        ],
    ),
    (
        "Seguimiento de leads",
        "Dar seguimiento a prospectos que no han concretado su inscripción. "
        "Contactar por WhatsApp/llamada y registrar resultados.",
        "media",
        MON_SAT,
        30,
        [
            "Revisar lista de leads pendientes",
            "Contactar leads del día anterior",
            "Registrar resultado de cada contacto",
            "Actualizar estatus (interesado / no interesado / inscrito)",
            "Agendar seguimiento próximo si aplica",
        ],
    ),
    (
        "Seguimiento de clases muestra",
        "Confirmar clases muestra agendadas para el día. Dar seguimiento a quienes "
        "tomaron clase muestra y aún no se inscriben.",
        "media",
        MON_SAT,
        30,
        [
            "Confirmar clases muestra del día (llamada/WhatsApp)",
            "Recibir prospectos en clase muestra",
            "Registrar asistencia a clase muestra",
            "Dar seguimiento a clase muestra de ayer",
            "Registrar decisión del prospecto",
        ],
    ),
]


class Command(BaseCommand):
    help = "Load initial catalog data: branches, roles, task modules, reception tasks, and default users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing data before loading (use with caution).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Resetting catalog data..."))
            from apps.tasks.models import TaskChecklist, Task, TaskModule
            from apps.roles.models import Role
            from apps.branches.models import Branch
            TaskChecklist.objects.all().delete()
            Task.objects.all().delete()
            TaskModule.objects.all().delete()
            Role.objects.all().delete()
            Branch.objects.all().delete()

        self._load_branches()
        self._load_roles()
        self._load_task_modules()
        self._load_reception_tasks()
        self._ensure_default_users()

        self.stdout.write(self.style.SUCCESS("\n✓ Initial data loaded successfully."))
        self.stdout.write(
            "\nNext steps:\n"
            "  1. Log in at /usuarios/login/\n"
            "  2. Assign roles to users via /usuarios/lista/\n"
        )

    def _load_branches(self):
        from apps.branches.models import Branch
        for data in BRANCHES:
            obj, created = Branch.objects.get_or_create(
                code=data["code"],
                defaults=data,
            )
            status = "creada" if created else "ya existe"
            self.stdout.write(f"  Sucursal '{obj.name}': {status}")

    def _load_roles(self):
        from apps.roles.models import Role
        for data in ROLES:
            obj, created = Role.objects.get_or_create(
                name=data["name"],
                defaults=data,
            )
            if not created:
                # Update permissions in case they changed
                for field, val in data.items():
                    if field != "name":
                        setattr(obj, field, val)
                obj.save()
            status = "creado" if created else "actualizado"
            self.stdout.write(f"  Rol '{obj.name}': {status}")

    def _load_task_modules(self):
        from apps.tasks.models import TaskModule
        for data in TASK_MODULES:
            obj, created = TaskModule.objects.get_or_create(
                name=data["name"],
                defaults=data,
            )
            status = "creado" if created else "ya existe"
            self.stdout.write(f"  Módulo '{obj.name}': {status}")

    def _load_reception_tasks(self):
        from apps.tasks.models import Task, TaskModule, TaskChecklist
        from apps.branches.models import Branch

        try:
            module = TaskModule.objects.get(name="Recepción")
        except TaskModule.DoesNotExist:
            self.stdout.write(self.style.ERROR("  Módulo 'Recepción' no encontrado. Abortando tareas."))
            return

        branches = Branch.objects.filter(is_active=True)
        if not branches.exists():
            self.stdout.write(self.style.ERROR("  No hay sucursales activas. Abortando tareas."))
            return

        for branch in branches:
            self.stdout.write(f"\n  Tareas para sucursal '{branch.name}':")
            for i, (title, desc, priority, days, duration, checklist) in enumerate(RECEPTION_TASKS, 1):
                task, created = Task.objects.get_or_create(
                    title=title,
                    branch=branch,
                    defaults={
                        "description": desc,
                        "module": module,
                        "priority": priority,
                        "is_recurring": True,
                        "recurring_days": days,
                        "estimated_duration": duration,
                        "status": "pendiente",
                        "is_active": True,
                    },
                )
                status = "creada" if created else "ya existe"
                self.stdout.write(f"    {i}. {title}: {status}")

                # Add checklist items if task is new
                if created and checklist:
                    for order, item_text in enumerate(checklist, 1):
                        TaskChecklist.objects.create(
                            task=task,
                            item=item_text,
                            order=order,
                        )
                    self.stdout.write(f"       → {len(checklist)} ítems de checklist agregados")

    def _ensure_default_users(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        default_users = [
            {
                "username": "superadmin",
                "email": "superadmin@nindomanager.local",
                "password": "12345",
                "is_superuser": True,
                "is_staff": True,
                "is_active": True,
            },
            {
                "username": "admin",
                "email": "admin@nindomanager.local",
                "password": "12345",
                "is_superuser": False,
                "is_staff": True,
                "is_active": True,
            },
        ]

        for data in default_users:
            password = data.pop("password")
            username = data["username"]
            defaults = dict(data)
            user, created = User.objects.update_or_create(
                username=username,
                defaults=defaults,
            )
            user.set_password(password)
            user.save(update_fields=["password"])

            status = "creado" if created else "actualizado"
            role = "superusuario" if user.is_superuser else "administrador"
            self.stdout.write(f"  Usuario '{username}' ({role}): {status}")
