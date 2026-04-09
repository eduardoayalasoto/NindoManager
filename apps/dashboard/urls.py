from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.RedirectToDashboard.as_view(), name="root"),
    path("dashboard/", views.DashboardView.as_view(), name="index"),
]
