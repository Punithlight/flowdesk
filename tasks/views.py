from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

import csv

from employees.models import Employee

from .models import Task
from .forms import TaskUpdateForm


# ==========================================================
# HELPER
# ==========================================================

def get_employee_for_user(user):
    """
    Return Employee profile for the logged-in Django user.
    """

    return (
        Employee.objects
        .filter(user=user)
        .select_related("user")
        .first()
    )


def get_user_role(user):
    """
    Return normalized employee role.
    """

    employee = get_employee_for_user(user)

    if not employee or not employee.role:
        return ""

    return employee.role.strip().lower()


# ==========================================================
# MY TASKS - EMPLOYEE
# ==========================================================

@login_required
def my_task(request):

    employee = get_employee_for_user(request.user)

    if not employee:

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect("login")

    tasks = (
        Task.objects
        .filter(
            employee=employee
        )
        .select_related(
            "project",
            "employee__user",
            "assigned_by"
        )
        .order_by(
            "due_date",
            "-created_at"
        )
    )

    pending_tasks = tasks.filter(
        status="Pending"
    )

    progress_tasks = tasks.filter(
        status="In Progress"
    )

    review_tasks = tasks.filter(
        status="Review"
    )

    completed_tasks = tasks.filter(
        status="Completed"
    )

    context = {

        "employee": employee,

        "tasks": tasks,

        "pending_tasks": pending_tasks,

        "progress_tasks": progress_tasks,

        "review_tasks": review_tasks,

        "completed_tasks": completed_tasks,

        "total_tasks": tasks.count(),

        "pending_count": pending_tasks.count(),

        "progress_count": progress_tasks.count(),

        "review_count": review_tasks.count(),

        "completed_count": completed_tasks.count(),
    }

    return render(
        request,
        "tasks/MyTask.html",
        context
    )


# ==========================================================
# UPDATE TASK
#
# EMPLOYEE:
#     Review → Team Lead Approval
#
# TEAM LEAD:
#     Review → Manager Approval
# ==========================================================

@login_required
def update_task(request, pk):

    employee = get_employee_for_user(request.user)

    if not employee:
        messages.error(
            request,
            "Employee profile not found."
        )
        return redirect("login")

    # User can update only their own assigned task
    task = get_object_or_404(
        Task,
        pk=pk,
        employee=employee
    )

    if request.method == "POST":

        form = TaskUpdateForm(
            request.POST,
            request.FILES,
            instance=task
        )

        if form.is_valid():

            updated_task = form.save(commit=False)

            role = (
                employee.role.strip().lower()
                if employee.role
                else ""
            )

            # ==================================================
            # EMPLOYEE / TEAM LEAD SUBMITS FOR REVIEW
            # ==================================================

            if updated_task.status == "Review":

                updated_task.approval_status = "Pending"
                updated_task.approved_at = None

                # ----------------------------------------------
                # NORMAL EMPLOYEE
                # Employee → Team Lead
                # ----------------------------------------------

                if role != "team lead":

                    updated_task.approval_stage = "TEAM_LEAD"

                # ----------------------------------------------
                # TEAM LEAD
                # Team Lead → Manager
                # ----------------------------------------------

                else:

                    updated_task.approval_stage = "MANAGER"

            # ==================================================
            # IN PROGRESS
            # ==================================================

            elif updated_task.status == "In Progress":

                updated_task.approved_at = None

                if updated_task.approval_status == "Pending":

                    updated_task.approval_status = "Rejected"

                # Keep the correct approval stage.
                #
                # Employee task → Team Lead
                # Team Lead task → Manager

                if role == "team lead":

                    updated_task.approval_stage = "MANAGER"

                else:

                    updated_task.approval_stage = "TEAM_LEAD"

            # ==================================================
            # EMPLOYEE / TEAM LEAD CANNOT DIRECTLY COMPLETE
            # ==================================================

            elif updated_task.status == "Completed":

                updated_task.status = "Review"

                updated_task.approval_status = "Pending"

                updated_task.approved_at = None

                if role == "team lead":

                    updated_task.approval_stage = "MANAGER"

                else:

                    updated_task.approval_stage = "TEAM_LEAD"

            updated_task.save()

            # ==================================================
            # SUCCESS MESSAGE
            # ==================================================

            if updated_task.status == "Review":

                if updated_task.approval_stage == "MANAGER":

                    messages.success(
                        request,
                        f'Task "{updated_task.title}" has been submitted for manager approval.'
                    )

                else:

                    messages.success(
                        request,
                        f'Task "{updated_task.title}" has been submitted for team lead approval.'
                    )

            else:

                messages.success(
                    request,
                    f'Task "{updated_task.title}" has been updated successfully.'
                )

            # ==================================================
            # REDIRECT
            # ==================================================

            if role == "team lead":

                return redirect("team_mytaskpage")

            return redirect("my_task")

    else:

        form = TaskUpdateForm(
            instance=task
        )

    return render(
        request,
        "tasks/update_task.html",
        {
            "task": task,
            "form": form,
            "employee": employee,
        }
    )

# ==========================================================
# TASK DETAIL
# ==========================================================

@login_required
def task_detail(request, pk):

    employee = get_employee_for_user(request.user)

    if not employee:

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect("login")

    task = get_object_or_404(
        Task.objects.select_related(
            "project",
            "employee__user",
            "assigned_by"
        ),
        pk=pk,
        employee=employee
    )

    return render(
        request,
        "tasks/task_detail.html",
        {
            "task": task,
            "employee": employee,
        }
    )


# ==========================================================
# EXPORT MY TASKS
# ==========================================================

@login_required
def export(request):

    employee = get_employee_for_user(request.user)

    if not employee:

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect("login")

    tasks = (
        Task.objects
        .filter(
            employee=employee
        )
        .select_related(
            "project",
            "assigned_by"
        )
        .order_by(
            "due_date"
        )
    )

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="my_tasks.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Task",
        "Project",
        "Description",
        "Priority",
        "Status",
        "Progress",
        "Due Date",
        "Assigned By",
        "Employee Comment",
        "Approval Status",
    ])

    for task in tasks:

        assigned_by = ""

        if task.assigned_by:

            assigned_by = (
                task.assigned_by.get_full_name()
                or task.assigned_by.username
            )

        project_name = ""

        if task.project:

            project_name = task.project.project_name

        writer.writerow([
            task.title,
            project_name,
            task.description or "",
            task.priority,
            task.status,
            f"{task.progress}%",
            task.due_date,
            assigned_by,
            task.employee_comment or "",
            task.approval_status,
        ])

    return response


# ==========================================================
# APPROVAL DASHBOARD
#
# This is the dashboard shown to manager/team lead.
# ==========================================================

@login_required
def approval_dashboard(request):

    role = get_user_role(request.user)

    # ======================================================
    # TEAM LEAD
    #
    # Team Lead approves tasks assigned by themselves
    # to employees.
    # ======================================================

    if role == "team lead":

        approval_tasks = (
            Task.objects
            .filter(
                assigned_by=request.user,
                status="Review",
                approval_status="Pending",
                approval_stage="TEAM_LEAD"
            )
            .select_related(
                "employee__user",
                "project",
                "assigned_by"
            )
        )
        

    # ======================================================
    # MANAGER
    #
    # Manager approves tasks assigned by Team Leads.
    #
    # For manager approval we need to exclude tasks created
    # by the manager themselves.
    # ======================================================

    elif role == "manager":

        approval_tasks = (
            Task.objects
            .filter(
                status="Review",
                approval_status="Pending",
                approval_stage="MANAGER"
            )
            
            
            .select_related(
                "employee__user",
                "project",
                "assigned_by"
            )
        )

    else:

        messages.error(
            request,
            "You do not have permission to access approvals."
        )

        return redirect("login")

    pending_count = approval_tasks.count()

    approved_queryset = Task.objects.none()

    rejected_queryset = Task.objects.none()

    awaiting_queryset = approval_tasks

    urgent_queryset = approval_tasks.filter(
        priority="High"
    )

    context = {

        "pending_count": pending_count,

        "approved_count": approved_queryset.count(),

        "rejected_count": rejected_queryset.count(),

        "awaiting_count": awaiting_queryset.count(),

        "urgent_count": urgent_queryset.count(),

        "pending_leave": 0,

        "pending_timesheet": 0,

        "pending_task": pending_count,

        "pending_tasks": approval_tasks,

        "approved_tasks": approved_queryset,

        "rejected_tasks": rejected_queryset,

        "awaiting_tasks": awaiting_queryset,

        "urgent_tasks": urgent_queryset,

        "role": role,
    }

    return render(
        request,
        "tasks/approval.html",
        context
    )


# ==========================================================
# TASK APPROVAL
#
# TEAM LEAD:
#     Employee → Team Lead
#
# MANAGER:
#     Team Lead → Manager
# ==========================================================

@login_required
def task_approval(request):

    role = get_user_role(request.user)

    # ------------------------------------------------------
    # TEAM LEAD APPROVAL
    # ------------------------------------------------------

    if role == "team lead":

        tasks = (
            Task.objects
            .filter(
                assigned_by=request.user,
                status="Review",
                approval_status="Pending"
            )
            .select_related(
                "project",
                "employee__user",
                "assigned_by"
            )
            .order_by(
                "due_date",
                "-created_at"
            )
        )

    # ------------------------------------------------------
    # MANAGER APPROVAL
    # ------------------------------------------------------

    elif role == "manager":

        tasks = (
            Task.objects
            .filter(
                status="Review",
                approval_status="Pending"
            )
            .exclude(
                assigned_by=request.user
            )
            .select_related(
                "project",
                "employee__user",
                "assigned_by"
            )
            .order_by(
                "due_date",
                "-created_at"
            )
        )

    else:

        messages.error(
            request,
            "You do not have permission to access task approval."
        )

        return redirect("login")

    return render(
        request,
        "tasks/task_approval.html",
        {
            "tasks": tasks,
            "pending_count": tasks.count(),
            "role": role,
        }
    )


# ==========================================================
# TASK COMPLETION APPROVAL
#
# TEAM LEAD:
#     Approves employee tasks
#
# MANAGER:
#     Approves team lead tasks
# ==========================================================

@login_required
def task_completion_approval(request):

    role = get_user_role(request.user)

    # ======================================================
    # TEAM LEAD APPROVAL
    #
    # Employee submitted task.
    #
    # Only tasks waiting for TEAM LEAD approval.
    # ======================================================

    if role == "team lead":

        pending_tasks = (
            Task.objects
            .filter(
                assigned_by=request.user,
                status="Review",
                approval_status="Pending",
                approval_stage="TEAM_LEAD"
            )
            .select_related(
                "employee__user",
                "project",
                "assigned_by"
            )
            .order_by(
                "due_date",
                "-created_at"
            )
        )

    # ======================================================
    # MANAGER APPROVAL
    #
    # Team Lead submitted task.
    #
    # ONLY approval_stage = MANAGER
    # ======================================================

    elif role == "manager":

        pending_tasks = (
            Task.objects
            .filter(
                status="Review",
                approval_status="Pending",
                approval_stage="MANAGER"
            )
            .select_related(
                "employee__user",
                "project",
                "assigned_by"
            )
            .order_by(
                "due_date",
                "-created_at"
            )
        )

    else:

        messages.error(
            request,
            "You do not have permission to access task completion approval."
        )

        return redirect("login")

    # ======================================================
    # SELECTED TASK
    # ======================================================

    selected_task = None

    task_id = request.GET.get("task")

    if task_id:

        # --------------------------------------------------
        # TEAM LEAD
        # --------------------------------------------------

        if role == "team lead":

            selected_task = get_object_or_404(
                Task.objects.select_related(
                    "employee__user",
                    "project",
                    "assigned_by"
                ),
                id=task_id,
                assigned_by=request.user,
                status="Review",
                approval_status="Pending",
                approval_stage="TEAM_LEAD"
            )

        # --------------------------------------------------
        # MANAGER
        # --------------------------------------------------

        elif role == "manager":

            selected_task = get_object_or_404(
                Task.objects.select_related(
                    "employee__user",
                    "project",
                    "assigned_by"
                ),
                id=task_id,
                status="Review",
                approval_status="Pending",
                approval_stage="MANAGER"
            )

    context = {
        "pending_tasks": pending_tasks,
        "selected_task": selected_task,
        "role": role,
    }

    return render(
        request,
        "tasks/task_completion_approval.html",
        context
    )

# ==========================================================
# APPROVE COMPLETED TASK
#
# TEAM LEAD:
#     Employee task → Completed
#
# MANAGER:
#     Team Lead task → Completed
# ==========================================================

@login_required
def approve_completed_task(request, pk):

    role = get_user_role(request.user)

    if request.method != "POST":

        return redirect(
            "task_completion_approval"
        )

    # ======================================================
    # TEAM LEAD
    #
    # Employee → Team Lead → Manager
    #
    # Team Lead DOES NOT complete the task.
    # Team Lead moves it to MANAGER approval.
    # ======================================================

    if role == "team lead":

        task = get_object_or_404(
            Task,
            pk=pk,
            assigned_by=request.user,
            status="Review",
            approval_status="Pending",
            approval_stage="TEAM_LEAD"
        )

        manager_notes = request.POST.get(
            "manager_notes",
            ""
        ).strip()

        if manager_notes:

            task.manager_comment = manager_notes

        # ----------------------------------------------
        # Move to Manager approval
        # ----------------------------------------------

        task.approval_status = "Pending"

        task.approval_stage = "MANAGER"

        task.status = "Review"

        task.approved_at = None

        task.save()

        messages.success(
            request,
            f'Task "{task.title}" has been forwarded to manager approval.'
        )

        return redirect(
            "task_completion_approval"
        )

    # ======================================================
    # MANAGER
    #
    # Manager performs FINAL approval.
    # ======================================================

    elif role == "manager":

        task = get_object_or_404(
            Task,
            pk=pk,
            status="Review",
            approval_status="Pending",
            approval_stage="MANAGER"
        )

        manager_notes = request.POST.get(
            "manager_notes",
            ""
        ).strip()

        # ----------------------------------------------
        # FINAL APPROVAL
        # ----------------------------------------------

        task.approval_status = "Approved"

        task.approval_stage = "COMPLETED"

        task.status = "Completed"

        task.manager_comment = manager_notes

        task.approved_at = timezone.now()

        # Make sure completed task is 100%
        if task.progress < 100:

            task.progress = 100

        task.save()

        messages.success(
            request,
            f'Task "{task.title}" has been approved successfully and completed.'
        )

        return redirect(
            "task_completion_approval"
        )

    else:

        messages.error(
            request,
            "You do not have permission to approve tasks."
        )

        return redirect("login")


# ==========================================================
# REJECT COMPLETED TASK
#
# TEAM LEAD:
#     Employee task → In Progress
#
# MANAGER:
#     Team Lead task → In Progress
# ==========================================================

@login_required
def reject_completed_task(request, pk):

    role = get_user_role(request.user)

    if request.method != "POST":

        return redirect(
            "task_completion_approval"
        )

    # ======================================================
    # TEAM LEAD REJECTION
    #
    # Employee task was waiting for Team Lead.
    # ======================================================

    if role == "team lead":

        task = get_object_or_404(
            Task,
            pk=pk,
            assigned_by=request.user,
            status="Review",
            approval_status="Pending",
            approval_stage="TEAM_LEAD"
        )

    # ======================================================
    # MANAGER REJECTION
    #
    # Team Lead task was waiting for Manager.
    # ======================================================

    elif role == "manager":

        task = get_object_or_404(
            Task,
            pk=pk,
            status="Review",
            approval_status="Pending",
            approval_stage="MANAGER"
        )

    else:

        messages.error(
            request,
            "You do not have permission to reject tasks."
        )

        return redirect("login")

    # ======================================================
    # COMMENT
    # ======================================================

    manager_comment = request.POST.get(
        "manager_comment",
        ""
    ).strip()

    # ======================================================
    # REJECT
    # ======================================================

    task.status = "In Progress"

    task.approval_status = "Rejected"

    task.approved_at = None

    if manager_comment:

        task.manager_comment = manager_comment

    task.save()

    messages.warning(
        request,
        f'Task "{task.title}" was rejected and returned for correction.'
    )

    return redirect(
        "task_completion_approval"
    )

# ==========================================================
# TIMESHEET APPROVAL
# ==========================================================

@login_required
def timesheet_approval(request):

    return render(
        request,
        "tasks/timesheet_approval.html",
        {
            "timesheets": [],
            "pending_count": 0,
        }
    )


# ==========================================================
# APPROVE TIMESHEET
# ==========================================================

@login_required
def approve_timesheet(request, pk):

    messages.error(
        request,
        "Timesheet approval is not connected to a Timesheet model yet."
    )

    return redirect(
        "timesheet_approval"
    )


# ==========================================================
# REJECT TIMESHEET
# ==========================================================

@login_required
def reject_timesheet(request, pk):

    messages.error(
        request,
        "Timesheet rejection is not connected to a Timesheet model yet."
    )

    return redirect(
        "timesheet_approval"
    )


# ==========================================================
# TEAM LEAD MY TASK PAGE
# ==========================================================

@login_required(login_url="login")
def team_mytaskpage(request):

    team_lead = Employee.objects.filter(
        user=request.user,
        role__iexact="Team Lead"
    ).first()

    if not team_lead:

        messages.error(
            request,
            "Team Lead profile not found."
        )

        return redirect("login")

    # ------------------------------------------------------
    # ONLY TASKS ASSIGNED TO THIS TEAM LEAD
    # ------------------------------------------------------

    my_tasks = (
        Task.objects
        .filter(
            employee=team_lead
        )
        .select_related(
            "project",
            "employee",
            "assigned_by"
        )
        .order_by(
            "due_date",
            "-created_at"
        )
    )

    todo_tasks = my_tasks.filter(
        status__in=[
            "Pending",
            "To Do"
        ]
    )

    inprogress_tasks = my_tasks.filter(
        status="In Progress"
    )

    review_tasks = my_tasks.filter(
        status="Review"
    )

    completed_tasks = my_tasks.filter(
        status="Completed"
    )

    context = {

        "team_lead": team_lead,

        "employee": team_lead,

        "my_tasks": my_tasks,

        "todo_tasks": todo_tasks,

        "in_progress_tasks": inprogress_tasks,

        "inprogress_tasks": inprogress_tasks,

        "review_tasks": review_tasks,

        "completed_tasks": completed_tasks,

    }

    return render(
        request,
        "tasks/team_Mytask.html",
        context
    )