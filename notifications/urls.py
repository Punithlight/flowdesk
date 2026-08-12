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
        "teamlead/",
        views.team_lead_notifications,
        name="teamlead_notifications"
    ),

    path(
        "mark-read/<int:id>/",
        views.mark_read,
        name="mark_read"
    ),

    # NEW - Team Lead dashboard bell
    path(
        "api/teamlead-unread/",
        views.teamlead_unread_notifications,
        name="teamlead_unread_notifications"
    ),
]