from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.teamlead_profile,
        name="teamlead_profile"
    ),
    path(
        "employees/",
        views.teamlead_employees,
        name="teamlead_employees"
    ),
    path(
        "task-management/",
        views.task_management,
        name="task_management"
    ),
]