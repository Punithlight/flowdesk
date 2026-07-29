from django.urls import path
from . import views

urlpatterns = [
    path("", views.employee_timesheet, name="employee_timesheet"),
]