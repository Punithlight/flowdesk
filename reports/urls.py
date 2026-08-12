from django.urls import path

from . import views


app_name = "reports"


urlpatterns = [

    # Employee reports
    path(
        "task-report/",
        views.task_report,
        name="task_report",
    ),

    # Submit report
    path(
        "submit/",
        views.submit_report,
        name="submit_report",
    ),

    # Team Lead reports
    path(
        "teamlead-reports/",
        views.teamlead_reports,
        name="teamlead_reports",
    ),

    # Reporting Center
    path(
        "reporting-center/",
        views.reporting_center,
        name="reporting_center",
    ),

    # Report detail
    path(
        "detail/<int:report_id>/",
        views.report_detail,
        name="report_detail",
    ),

    # Delete
    path(
        "delete/<int:report_id>/",
        views.delete_report,
        name="delete_report",
    ),
]