import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from employees.models import Employee
from tasks.models import Task
from .models import Project


# ==========================================================
# PROJECT DASHBOARD STATS
# ==========================================================

def _project_stats():
    today = timezone.now().date()

    return {
        "total_projects": Project.objects.count(),
        "active_projects": Project.objects.filter(
            status="in_progress"
        ).count(),

        "completed_projects": Project.objects.filter(
            status="completed"
        ).count(),

        "overdue_projects": Project.objects.filter(
            end_date__lt=today
        ).exclude(
            status="completed"
        ).count(),
    }


# ==========================================================
# GET EMPLOYEE FROM HIDDEN JSON
# ==========================================================

def _resolve_assignee_user(assignee_details_raw):

    if not assignee_details_raw:
        return None, None

    try:
        details = json.loads(
            assignee_details_raw
        )
    except json.JSONDecodeError:
        return None, None

    email = details.get(
        "email",
        ""
    ).strip()

    employee = Employee.objects.filter(
        user__email=email
    ).first()

    return employee, details


# ==========================================================
# EMPLOYEE PROJECTS
# ==========================================================

@login_required
def Myprojects(request):

    projects = Project.objects.filter(
        employee=request.user,
        project_type="Project"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "projects/Myprojects.html",
        {
            "projects": projects,
            "total_projects": projects.count(),
        }
    )


# ==========================================================
# CREATE PROJECT / TASK
# ==========================================================

@login_required
def create_project(request):

    manager = Employee.objects.filter(
        user=request.user
    ).first()

    if not manager:

        messages.error(
            request,
            "Manager profile not found."
        )

        return redirect("login")

    team_leads = Employee.objects.filter(
        role="Team Lead"
    ).order_by(
        "department"
    )

    employees = Employee.objects.filter(
        role="Employee"
    ).order_by(
        "user__first_name"
    )

    existing_projects = Project.objects.filter(
        project_type="Project"
    ).order_by(
        "-created_at"
    )

    context = {
        "team_leads": team_leads,
        "employees": employees,
        "existing_projects": existing_projects,
        **_project_stats(),
    }

    if request.method != "POST":
        return render(
            request,
            "projects/create_project.html",
            context
        )

    # ==================================================
    # FORM DATA
    # ==================================================

    project_type = request.POST.get(
        "projectType"
    )

    title = request.POST.get(
        "title",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    start_date = request.POST.get(
        "start_date"
    )

    end_date = (
        request.POST.get("end_date")
        or start_date
    )

    linked_project_id = request.POST.get(
        "linked_project"
    )

    attachment = request.FILES.get(
        "attachment"
    )

    assignee_details = request.POST.get(
        "assigneeDetails",
        ""
    )

    employee_obj, details = _resolve_assignee_user(
        assignee_details
    )

    assignee_user = (
        employee_obj.user
        if employee_obj
        else None
    )

    assignee_role = (
        details.get("role", "")
        if details
        else ""
    )

    # ==================================================
    # VALIDATION
    # ==================================================

    if not title:

        messages.error(
            request,
            "Title is required."
        )

        return render(
            request,
            "projects/create_project.html",
            context
        )

    if not description:

        messages.error(
            request,
            "Description is required."
        )

        return render(
            request,
            "projects/create_project.html",
            context
        )

    if not start_date:

        messages.error(
            request,
            "Start date is required."
        )

        return render(
            request,
            "projects/create_project.html",
            context
        )

    if employee_obj is None:

        messages.error(
            request,
            "Please select a valid employee."
        )

        return render(
            request,
            "projects/create_project.html",
            context
        )