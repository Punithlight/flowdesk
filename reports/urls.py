from django.urls import path

from . import views


# ============================================================
# REPORTS APP NAMESPACE
# ============================================================

app_name = "reports"


urlpatterns = [

    # ========================================================
    # REPORTING CENTER
    # Manager Dashboard -> Reports
    # ========================================================

    path(
        "reporting-center/",
        views.reporting_center,
        name="reporting_center",
    ),


    # ========================================================
    # SUBMIT REPORT
    # Employee / Manager -> Submit Report
    # ========================================================

    path(
        "submit/",
        views.submit_report,
        name="submit_report",
    ),


    # ========================================================
    # REPORT DETAIL
    # ========================================================

    path(
        "report/<int:report_id>/",
        views.report_detail,
        name="report_detail",
    ),


    # ========================================================
    # DELETE REPORT
    # ========================================================

    path(
        "report/<int:report_id>/delete/",
        views.delete_report,
        name="delete_report",
    ),


    # ========================================================
    # EMPLOYEE TASK REPORT
    # Employee Dashboard -> Task Report
    # ========================================================

    path(
        "task-report/",
        views.task_report,
        name="task_report",
    ),
]