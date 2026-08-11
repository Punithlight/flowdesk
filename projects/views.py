import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
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
# RESOLVE EMPLOYEE
# ==========================================================

def _resolve_assignee_user(assignee_details_raw):

    if not assignee_details_raw:
        return None, None

    try:
        details = json.loads(
            assignee_details_raw
        )

    except (json.JSONDecodeError, TypeError):
        return None, None

    # ------------------------------------------------------
    # FIRST TRY EMPLOYEE ID
    # ------------------------------------------------------

    employee_id = details.get("employee_id")

    if employee_id:

        employee = Employee.objects.filter(
            id=employee_id
        ).select_related(
            "user"
        ).first()

        if employee:
            return employee, details

    # ------------------------------------------------------
    # FALLBACK TO EMAIL
    # ------------------------------------------------------

    email = details.get(
        "email",
        ""
    ).strip()

    if email:

        employee = Employee.objects.filter(
            user__email__iexact=email
        ).select_related(
            "user"
        ).first()

        if employee:
            return employee, details

    return None, details


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
# CREATE PROJECT / ASSIGN TASK
# ==========================================================

@login_required
def create_project(request):

    # ------------------------------------------------------
    # CURRENT USER EMPLOYEE PROFILE
    # ------------------------------------------------------

    manager = Employee.objects.filter(
        user=request.user
    ).first()

    if not manager:

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect("login")

    # ------------------------------------------------------
    # TEAM LEADS
    # ------------------------------------------------------

    team_leads = Employee.objects.filter(
        role="Team Lead"
    ).select_related(
        "user"
    ).order_by(
        "department"
    )

    # ------------------------------------------------------
    # EMPLOYEES
    #
    # IMPORTANT:
    # Use case-insensitive matching so that values such as
    # Employee / employee do not cause an empty dropdown.
    # ------------------------------------------------------

    employees = Employee.objects.filter(
        role__iexact="Employee"
    ).select_related(
        "user"
    ).order_by(
        "user__first_name",
        "user__last_name"
    )

    # ------------------------------------------------------
    # EXISTING PROJECTS
    # ------------------------------------------------------

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

    # ======================================================
    # GET
    # ======================================================

    if request.method != "POST":

        return render(
            request,
            "projects/create_project.html",
            context
        )

    # ======================================================
    # FORM DATA
    # ======================================================

    project_type = request.POST.get(
        "projectType",
        ""
    ).strip()

    title = request.POST.get(
        "title",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    start_date = request.POST.get(
        "start_date",
        ""
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

    # ------------------------------------------------------
    # RESOLVE EMPLOYEE
    # ------------------------------------------------------

    employee_obj, details = _resolve_assignee_user(
        assignee_details
    )

    # ======================================================
    # VALIDATION
    # ======================================================

    if project_type not in [
        "Project",
        "Task"
    ]:

        messages.error(
            request,
            "Please select Project or Task."
        )

        return render(
            request,
            "projects/create_project.html",
            context
        )

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

    if not employee_obj:

        messages.error(
            request,
            "Please select a valid employee."
        )

        return render(
            request,
            "projects/create_project.html",
            context
        )

    # ======================================================
    # CREATE PROJECT
    # ======================================================

    if project_type == "Project":

        assignee_user = employee_obj.user

        assignee_role = employee_obj.role

        Project.objects.create(
            project_name=title,
            description=description,
            employee=assignee_user,
            role=assignee_role,
            start_date=start_date,
            end_date=end_date,
            status="pending",
            project_type="Project",
        )

        messages.success(
            request,
            "Project created successfully."
        )

        return redirect(
            "Myprojects"
        )

    # ======================================================
    # CREATE TASK
    # ======================================================

    project = None

    if linked_project_id:

        project = Project.objects.filter(
            id=linked_project_id
        ).first()

    Task.objects.create(

        project=project,

        employee=employee_obj,

        assigned_by=request.user,

        title=title,

        description=description,

        priority="Medium",

        status="Pending",

        due_date=end_date,

        attachment=attachment,
    )

    messages.success(
        request,
        f"Task assigned successfully to "
        f"{employee_obj.user.get_full_name() or employee_obj.user.username}."
    )

    return redirect(
        "create_project"
    )


# ==========================================================
# TEAM LEAD PROJECTS / ASSIGN TASK
#
# This is the ONLY definition of this page. It used to be
# duplicated in dashboard/views.py (with richer GET context)
# and here (with a thinner, incorrect GET filter and no POST
# handling at all -- so the "Assign Project / Task" form on
# this page silently did nothing). Both are merged into one
# correct view that actually saves what the team lead submits.
# ==========================================================

@login_required
def teamlead_projects(request):
 
    # ------------------------------------------------------
    # LOGGED-IN TEAM LEAD
    # ------------------------------------------------------
 
    teamlead = Employee.objects.filter(
        user=request.user,
        role__iexact="Team Lead"
    ).select_related("user").first()
 
    if not teamlead:
 
        messages.error(
            request,
            "Team Lead profile not found."
        )
 
        return redirect("login")
 
    # ------------------------------------------------------
    # EMPLOYEES AVAILABLE TO ASSIGN
    # ------------------------------------------------------
 
    employees = Employee.objects.filter(
        role__iexact="Employee"
    ).select_related("user").order_by(
        "user__first_name",
        "user__last_name"
    )
 
    # ------------------------------------------------------
    # ALL PROJECTS (for the "link to project" dropdown)
    # ------------------------------------------------------
 
    projects = Project.objects.all().order_by("-id")
 
    # ======================================================
    # POST: ASSIGN A PROJECT OR TASK TO AN EMPLOYEE
    # ======================================================
 
    if request.method == "POST":
 
        project_type = request.POST.get("projectType", "").strip()
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        linked_project_id = request.POST.get("project", "").strip()
        employee_id = request.POST.get("employee", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        due_date = request.POST.get("due_date", "").strip()
        attachment = request.FILES.get("attachment")
 
        assignee = employees.filter(id=employee_id).first()
 
        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------
 
        if project_type not in ["Project", "Task"]:
            messages.error(request, "Please select Project or Task.")
 
        elif not title:
            messages.error(request, "Please enter a title.")
 
        elif not due_date:
            messages.error(request, "Please select a due date.")
 
        elif not assignee:
            messages.error(request, "Please select a valid employee.")
 
        else:
 
            # ------------------------------------------------
            # CREATE PROJECT
            # ------------------------------------------------
 
            if project_type == "Project":
 
                Project.objects.create(
                    project_name=title,
                    description=description,
                    employee=assignee.user,
                    role=assignee.role,
                    start_date=start_date or timezone.localdate(),
                    end_date=due_date,
                    status="pending",
                    project_type="Project",
                )
 
                messages.success(
                    request,
                    f"Project \"{title}\" assigned to "
                    f"{assignee.user.get_full_name() or assignee.user.username}."
                )
 
            # ------------------------------------------------
            # CREATE TASK
            # ------------------------------------------------
 
            else:
 
                linked_project = None
 
                if linked_project_id:
                    linked_project = projects.filter(
                        id=linked_project_id
                    ).first()
 
                Task.objects.create(
                    project=linked_project,
                    employee=assignee,
                    assigned_by=request.user,
                    title=title,
                    description=description,
                    priority="Medium",
                    status="Pending",
                    start_date=start_date or None,
                    due_date=due_date,
                    attachment=attachment,
                )
 
                messages.success(
                    request,
                    f"Task \"{title}\" assigned to "
                    f"{assignee.user.get_full_name() or assignee.user.username}."
                )
 
            return redirect("teamlead_projects")
 
    # ======================================================
    # GET: PAGE + STATS
    # ======================================================
 
    total_projects = projects.count()
 
    active_projects = projects.filter(
        status__iexact="in_progress"
    ).count()
 
    completed_projects = projects.filter(
        status__iexact="completed"
    ).count()
 
    overdue_projects = projects.filter(
        end_date__lt=timezone.localdate()
    ).exclude(
        status__iexact="completed"
    ).count()
 
    context = {
        "employee": teamlead,
        "teamlead": teamlead,
        "employees": employees,
        "projects": projects,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "overdue_projects": overdue_projects,
    }
 
    return render(
        request,
        "projects/teamlead_projects.html",
        context
    )
 