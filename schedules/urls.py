from django.urls import path
from . import views


app_name = "schedules"


urlpatterns = [

    path(
        "manager/",
        views.manager_schedules,
        name="manager_schedules"
    ),

    path(
        "employee/",
        views.employee_schedules,
        name="employee_schedules"
    ),

    path(
        "create/",
        views.create_schedule,
        name="create_schedule"
    ),

    path(
        "delete/<int:id>/",
        views.delete_schedule,
        name="delete_schedule"
    ),
    path(
        "notify/<int:pk>/",
        views.notify_attendees,
        name="notify_attendees"
),

]