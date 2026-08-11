from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from employees.models import Employee

from .models import Report


# ============================================================
# HELPER
# ============================================================

def get_current_employee(request):

    return (
        Employee.objects
        .filter(
            user=request.user
        )
        .select_related(
            "user"
        )
        .first()
    )


# ============================================================
# REPORTING CENTER
#
# Manager Dashboard -> Reports
#
# Shows:
#   1. Employee Reports
#   2. Manager / Team Lead Reports
# ============================================================

@login_required
def reporting_center(request):

    # ========================================================
    # EMPLOYEE REPORTS
    # ========================================================

    employee_reports = (
        Report.objects
        .filter(
            report_type="employee",
            status__in=[
                "submitted",
                "sent",
            ],
        )
        .select_related(
            "employee",
            "employee__user",
        )
        .order_by(
            "-created_at"
        )
    )


    # ========================================================
    # MANAGER / TEAM LEAD REPORTS
    # ========================================================

    manager_reports = (
        Report.objects
        .filter(
            report_type="manager",
            status__in=[
                "submitted",
                "sent",
            ],
        )
        .select_related(
            "employee",
            "employee__user",
        )
        .order_by(
            "-created_at"
        )
    )


    # ========================================================
    # DEPARTMENTS
    #
    # Get departments from BOTH:
    #
    # 1. Employee table
    # 2. Submitted reports
    #
    # This ensures that a report submitted under
    # "Python" appears even if the Employee table
    # currently contains "General".
    # ========================================================

    employee_departments_from_db = (
        Employee.objects
        .exclude(
            department=""
        )
        .values_list(
            "department",
            flat=True,
        )
        .distinct()
    )


    employee_report_departments = (
        employee_reports
        .exclude(
            department=""
        )
        .values_list(
            "department",
            flat=True,
        )
        .distinct()
    )


    manager_report_departments = (
        manager_reports
        .exclude(
            department=""
        )
        .values_list(
            "department",
            flat=True,
        )
        .distinct()
    )


    # ========================================================
    # COMBINE ALL DEPARTMENTS
    # ========================================================

    departments = sorted(
        set(employee_departments_from_db)
        | set(employee_report_departments)
        | set(manager_report_departments)
    )


    # ========================================================
    # EMPLOYEE REPORTS BY DEPARTMENT
    # ========================================================

    employee_departments = []

    for department in departments:

        reports = employee_reports.filter(
            department=department
        )

        employee_departments.append({
            "name": department,
            "reports": reports,
        })


    # ========================================================
    # MANAGER / TEAM LEAD REPORTS BY DEPARTMENT
    # ========================================================

    team_lead_departments = []

    for department in departments:

        reports = manager_reports.filter(
            department=department
        )

        team_lead_departments.append({
            "name": department,
            "reports": reports,
        })


    # ========================================================
    # STATISTICS
    # ========================================================

    total_employee_reports = (
        employee_reports.count()
    )


    total_manager_reports = (
        manager_reports.count()
    )


    total_reports = (
        total_employee_reports
        + total_manager_reports
    )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "employee_departments":
            employee_departments,

        "team_lead_departments":
            team_lead_departments,

        "total_employee_reports":
            total_employee_reports,

        "total_manager_reports":
            total_manager_reports,

        "total_reports":
            total_reports,

        "employee_reports":
            employee_reports,

        "manager_reports":
            manager_reports,
    }


    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "reports/reporting_center.html",
        context,
    )


# ============================================================
# EMPLOYEE TASK REPORT
#
# Employee Dashboard -> Task Report
# ============================================================

@login_required
def task_report(request):

    employee = get_current_employee(
        request
    )


    # ========================================================
    # EMPLOYEE CHECK
    # ========================================================

    if employee is None:

        messages.error(
            request,
            "Employee profile not found.",
        )

        return redirect(
            "reports:task_report"
        )


    # ========================================================
    # EMPLOYEE'S OWN REPORTS
    # ========================================================

    reports = (
        Report.objects
        .filter(
            employee=employee
        )
        .select_related(
            "employee",
            "employee__user",
        )
        .order_by(
            "-created_at"
        )
    )


    # ========================================================
    # STATISTICS
    # ========================================================

    total_reports = reports.count()

    submitted_reports = (
        reports
        .filter(
            status="submitted"
        )
        .count()
    )

    sent_reports = (
        reports
        .filter(
            status="sent"
        )
        .count()
    )

    draft_reports = (
        reports
        .filter(
            status="draft"
        )
        .count()
    )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "employee":
            employee,

        "reports":
            reports,

        "total_reports":
            total_reports,

        "submitted_reports":
            submitted_reports,

        "sent_reports":
            sent_reports,

        "draft_reports":
            draft_reports,
    }


    return render(
        request,
        "reports/task_report.html",
        context,
    )


# ============================================================
# SUBMIT REPORT
#
# Employee:
#     report_type = employee
#
# Manager / Team Lead:
#     can create employee or manager report
# ============================================================

@login_required
def submit_report(request):

    if request.method != "POST":

        return redirect(
            "reports:task_report"
        )


    employee = get_current_employee(
        request
    )


    # ========================================================
    # EMPLOYEE CHECK
    # ========================================================

    if employee is None:

        messages.error(
            request,
            "Employee profile not found.",
        )

        return redirect(
            "reports:task_report"
        )


    # ========================================================
    # FORM DATA
    # ========================================================

    department = request.POST.get(
        "department",
        "",
    ).strip()


    title = request.POST.get(
        "title",
        "",
    ).strip()


    report_text = request.POST.get(
        "reportText",
        "",
    ).strip()


    requested_type = request.POST.get(
        "report_type",
        "employee",
    ).strip().lower()


    action = request.POST.get(
        "action",
        "save",
    ).strip().lower()


    attachment = request.FILES.get(
        "attachment"
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if not department:

        messages.error(
            request,
            "Please select a department.",
        )

        return redirect(
            "reports:task_report"
        )


    if not title:

        messages.error(
            request,
            "Please enter a report title.",
        )

        return redirect(
            "reports:task_report"
        )


    if not report_text:

        messages.error(
            request,
            "Please enter the report details.",
        )

        return redirect(
            "reports:task_report"
        )


    # ========================================================
    # REPORT TYPE
    # ========================================================

    if employee.role in [
        "Manager",
        "Team Lead",
    ]:

        if requested_type == "manager":

            report_type = "manager"

        else:

            report_type = "employee"

    else:

        # Normal employees can only send
        # employee reports.

        report_type = "employee"


    # ========================================================
    # STATUS
    # ========================================================

    if action in [
        "send",
        "submit",
    ]:

        status = "sent"

        submitted_at = timezone.now()

    else:

        status = "draft"

        submitted_at = None


    # ========================================================
    # CREATE REPORT
    # ========================================================

    report = Report.objects.create(

        employee=employee,

        report_type=report_type,

        department=department,

        title=title,

        report_text=report_text,

        attachment=attachment,

        status=status,

        submitted_at=submitted_at,
    )


    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    if status == "draft":

        messages.success(
            request,
            "Report saved as draft.",
        )

    else:

        messages.success(
            request,
            "Report sent successfully to the manager.",
        )


    # ========================================================
    # REDIRECT
    # ========================================================

    return redirect(
    "reports:task_report"
    )


# ============================================================
# REPORT DETAIL
# ============================================================

@login_required
def report_detail(
    request,
    report_id,
):

    report = get_object_or_404(

        Report.objects.select_related(
            "employee",
            "employee__user",
        ),

        id=report_id,
    )


    return render(
        request,
        "reports/report_detail.html",
        {
            "report": report,
        },
    )


# ============================================================
# DELETE REPORT
# ============================================================

@login_required
def delete_report(
    request,
    report_id,
):

    report = get_object_or_404(
        Report,
        id=report_id,
    )


    employee = get_current_employee(
        request
    )


    # ========================================================
    # EMPLOYEE CHECK
    # ========================================================

    if employee is None:

        messages.error(
            request,
            "Employee profile not found.",
        )

        return redirect(
            "reports:task_report"
        )


    # ========================================================
    # PERMISSION
    # ========================================================

    can_delete = (

        report.employee_id == employee.id

        or employee.role in [
            "Manager",
            "Team Lead",
        ]
    )


    if not can_delete:

        messages.error(
            request,
            "You do not have permission to delete this report.",
        )

        return redirect(
            "reports:task_report"
        )


    # ========================================================
    # DELETE
    # ========================================================

    if request.method == "POST":

        if report.attachment:

            report.attachment.delete(
                save=False
            )


        report.delete()


        messages.success(
            request,
            "Report deleted successfully.",
        )


    # ========================================================
    # REDIRECT
    # ========================================================

    if employee.role in [
        "Manager",
        "Team Lead",
    ]:

        return redirect(
            "reports:reporting_center"
        )


    return redirect(
        "reports:task_report"
    )