from django.urls import path
from . import views

urlpatterns = [

    # Employee Timesheet
    path(
        "",
        views.employee_timesheet,
        name="employee_timesheet"
    ),

    # Submit Timesheet
    path(
        "submit/<int:pk>/",
        views.submit_timesheet,
        name="submit_timesheet"
    ),

    # Manager Timesheet Approval
    path(
        "approval/",
        views.manager_timesheets,
        name="timesheet_approval"
    ),

    # Approve Timesheet
    path(
        "approve/<int:pk>/",
        views.approve_timesheet,
        name="approve_timesheet"
    ),

    # Reject Timesheet
    path(
        "reject/<int:pk>/",
        views.reject_timesheet,
        name="reject_timesheet"
    ),

]