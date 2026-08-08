from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path(
        "",
        views.notification_list,
        name="list"
    ),

    path(
        "manager/",
        views.manager_notifications,
        name="manager_notifications"
    ),

    path(
        "mark-read/<int:id>/",
        views.mark_read,
        name="mark_read"
    ),
]