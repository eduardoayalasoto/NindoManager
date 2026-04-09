from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.TaskListView.as_view(), name="list"),
    path("hoy/", views.DailyTasksView.as_view(), name="daily"),
    path("nueva/", views.TaskCreateView.as_view(), name="create"),
    path("<int:pk>/", views.TaskDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.TaskUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", views.TaskDeleteView.as_view(), name="delete"),
    path("instancia/<int:pk>/", views.TaskInstanceDetailView.as_view(), name="instance_detail"),
    path("instancia/<int:pk>/iniciar/", views.TaskInstanceStartView.as_view(), name="instance_start"),
    path("instancia/<int:pk>/completar/", views.TaskInstanceCompleteView.as_view(), name="instance_complete"),
    path("checklist/<int:pk>/toggle/", views.ChecklistItemToggleView.as_view(), name="checklist_toggle"),
    path("generar-hoy/", views.GenerateTodayInstancesView.as_view(), name="generate_today"),
]
