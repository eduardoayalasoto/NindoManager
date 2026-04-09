from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="list"),
    path("<int:pk>/leer/", views.MarkNotificationReadView.as_view(), name="mark_read"),
    path("leer-todo/", views.MarkAllReadView.as_view(), name="mark_all_read"),
    path("contador/", views.UnreadCountView.as_view(), name="unread_count"),
]
