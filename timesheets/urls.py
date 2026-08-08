from django.urls import path
from . import views

urlpatterns = [
    path("", views.employee_timesheet, name="employee_timesheet"),

    path("add/<int:pk>/", views.add_entry, name="add_entry"),
    path("edit/<int:pk>/", views.edit_entry, name="edit_entry"),
    path("delete/<int:pk>/", views.delete_entry, name="delete_entry"),

    path("submit/<int:pk>/", views.submit_timesheet, name="submit_timesheet"),

    path("approval/", views.manager_timesheets, name="timesheet_approval"),

    path("approve/<int:pk>/", views.approve_timesheet, name="approve_timesheet"),

    path("reject/<int:pk>/", views.reject_timesheet, name="reject_timesheet"),
]