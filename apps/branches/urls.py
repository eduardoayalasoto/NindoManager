from django.urls import path
from . import views

app_name = "branches"

urlpatterns = [
    path("", views.BranchListView.as_view(), name="list"),
    path("<int:pk>/", views.BranchDetailView.as_view(), name="detail"),
    path("nueva/", views.BranchCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.BranchUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", views.BranchDeleteView.as_view(), name="delete"),
]
