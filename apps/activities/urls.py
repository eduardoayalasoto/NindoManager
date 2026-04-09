from django.urls import path
from . import views

app_name = "activities"

urlpatterns = [
    path("", views.ActivityListView.as_view(), name="list"),
    path("<int:pk>/", views.ActivityDetailView.as_view(), name="detail"),
    path("exportar/", views.ActivityExportView.as_view(), name="export"),
]
