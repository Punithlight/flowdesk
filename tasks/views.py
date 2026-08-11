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
    Get Employee profile for the logged-in Django user.
    """

    return (
        Employee.objects
        .filter(user=user)
        .select_related("user")
        .first()
    )


# ==========================================================
# MY TASKS
# EMPLOYEE DASHBOARD
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

    # ------------------------------------------------------
    # Tasks assigned to this employee
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Status groups
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Context
    # ------------------------------------------------------

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
# EMPLOYEE UPDATES THEIR OWN TASK
#
# FLOW:
#
# Pending
#    ↓
# In Progress
#    ↓
# Review
#    ↓
# Manager Approval
#    ↓
# Completed
#
# Rejected:
#
# Review
#    ↓
# Rejected
#    ↓
# In Progress
#    ↓
# Review
# ==========================================================

@login_required
def update_task(request, pk):

    # ------------------------------------------------------
    # Get logged-in employee
    # ------------------------------------------------------

    employee = get_employee_for_user(request.user)

    if not employee:

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect("login")

    # ------------------------------------------------------
    # SECURITY
    #
    # Employee can update ONLY their own task.
    # ------------------------------------------------------

    task = get_object_or_404(
        Task,
        pk=pk,
        employee=employee
    )

    # ------------------------------------------------------
    # POST
    # ------------------------------------------------------

    if request.method == "POST":

        form = TaskUpdateForm(
            request.POST,
            request.FILES,
            instance=task
        )

        if form.is_valid():

            # Do not save immediately.
            # We need to control approval workflow.
            updated_task = form.save(
                commit=False
            )

            # ==================================================
            # EMPLOYEE SUBMITS TASK FOR REVIEW
            # ==================================================
            #
            # When employee selects:
            #
            # Status = Review
            #
            # Automatically:
            #
            # approval_status = Pending
            #
            # This makes the task appear in the manager's
            # Task Completion Approval page.
            # ==================================================

            if updated_task.status == "Review":

                updated_task.approval_status = "Pending"

                updated_task.approved_at = None

            # ==================================================
            # EMPLOYEE WORKING ON TASK
            # ==================================================
            #
            # If employee moves it back to In Progress,
            # manager approval is no longer active.
            # ==================================================

            elif updated_task.status == "In Progress":

                # If it was previously rejected, keep the
                # rejected history until the employee submits
                # it again for Review.
                #
                # When Review is selected above, it becomes
                # Pending again.

                updated_task.approved_at = None

            # ==================================================
            # EMPLOYEE SHOULD NOT COMPLETE TASK DIRECTLY
            # ==================================================
            #
            # Completed should happen only after manager
            # approval.
            # ==================================================

            elif updated_task.status == "Completed":

                # Prevent employee from directly completing
                # a task.

                updated_task.status = "Review"

                updated_task.approval_status = "Pending"

                updated_task.approved_at = None

            # --------------------------------------------------
            # Save task
            # --------------------------------------------------

            updated_task.save()

            # --------------------------------------------------
            # Success message
            # --------------------------------------------------

            if updated_task.status == "Review":

                messages.success(
                    request,
                    f'Task "{updated_task.title}" has been submitted for manager approval.'
                )

            else:

                messages.success(
                    request,
                    f'Task "{updated_task.title}" has been updated successfully.'
                )

            # --------------------------------------------------
            # IMPORTANT
            #
            # After Save Changes:
            # GO TO MY TASK PAGE
            #
            # NOT Team Lead Projects page.
            # --------------------------------------------------

            return redirect(
                "my_task"
            )

    else:

        # ------------------------------------------------------
        # GET
        # ------------------------------------------------------

        form = TaskUpdateForm(
            instance=task
        )

    # ----------------------------------------------------------
    # Render Update Task page
    # ----------------------------------------------------------

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

    # ------------------------------------------------------
    # Employee can view ONLY their own task
    # ------------------------------------------------------

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

            project_name = (
                task.project.project_name
            )

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
# MANAGER / TEAM LEAD APPROVAL DASHBOARD
# ==========================================================

@login_required
def approval_dashboard(request):

    # ------------------------------------------------------
    # Tasks created by logged-in manager/team lead
    # ------------------------------------------------------

    manager_tasks = (
        Task.objects
        .filter(
            assigned_by=request.user
        )
        .select_related(
            "employee__user",
            "project",
            "assigned_by"
        )
    )

    # ======================================================
    # PENDING TASK APPROVALS
    #
    # Employee submitted task for review.
    # ======================================================

    pending_task_queryset = manager_tasks.filter(
        status="Review",
        approval_status="Pending"
    )

    # ======================================================
    # APPROVED TASKS
    # ======================================================

    approved_queryset = manager_tasks.filter(
        approval_status="Approved"
    )

    # ======================================================
    # REJECTED TASKS
    # ======================================================

    rejected_queryset = manager_tasks.filter(
        approval_status="Rejected"
    )

    # ======================================================
    # AWAITING REVIEW
    # ======================================================

    awaiting_queryset = manager_tasks.filter(
        status="Review",
        approval_status="Pending"
    )

    # ======================================================
    # URGENT TASKS
    # ======================================================

    urgent_queryset = manager_tasks.filter(
        priority="High",
        status="Review",
        approval_status="Pending"
    )

    # ======================================================
    # COUNTS
    # ======================================================

    pending_count = pending_task_queryset.count()

    approved_count = approved_queryset.count()

    rejected_count = rejected_queryset.count()

    awaiting_count = awaiting_queryset.count()

    urgent_count = urgent_queryset.count()

    # ======================================================
    # OTHER APPROVAL COUNTS
    # ======================================================

    pending_leave = 0

    pending_timesheet = 0

    pending_task = pending_count

    # ======================================================
    # CONTEXT
    # ======================================================

    context = {

        "pending_count": pending_count,

        "approved_count": approved_count,

        "rejected_count": rejected_count,

        "awaiting_count": awaiting_count,

        "urgent_count": urgent_count,

        "pending_leave": pending_leave,

        "pending_timesheet": pending_timesheet,

        "pending_task": pending_task,

        "pending_tasks": pending_task_queryset,

        "approved_tasks": approved_queryset,

        "rejected_tasks": rejected_queryset,

        "awaiting_tasks": awaiting_queryset,

        "urgent_tasks": urgent_queryset,
    }

    return render(
        request,
        "tasks/approval.html",
        context
    )


# ==========================================================
# TASK APPROVAL DASHBOARD
# ==========================================================

@login_required
def task_approval(request):

    # ------------------------------------------------------
    # Tasks created by this manager/team lead
    # ------------------------------------------------------

    tasks = (
        Task.objects
        .filter(
            assigned_by=request.user,
            approval_status="Pending",
            status="Review"
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

    return render(
        request,
        "tasks/task_approval.html",
        {
            "tasks": tasks,
            "pending_count": tasks.count(),
        }
    )


# ==========================================================
# TASK COMPLETION APPROVAL
#
# THIS IS THE MAIN MANAGER APPROVAL PAGE
# ==========================================================

@login_required
def task_completion_approval(request):

    # ------------------------------------------------------
    # Tasks waiting for manager approval
    # ------------------------------------------------------
    pending_tasks = (
        Task.objects
        .filter(
            status="Review",
            approval_status="Pending"
        )
        .select_related(
            "employee",
            "project",
            "assigned_by"
        )
        .order_by("due_date")
    )

    # ------------------------------------------------------
    # Selected task
    # ------------------------------------------------------
    selected_task = None

    task_id = request.GET.get("task")

    if task_id:
        selected_task = get_object_or_404(
            Task.objects.select_related(
                "employee",
                "project",
                "assigned_by"
            ),
            id=task_id,
            status="Review",
            approval_status="Pending"
        )

    context = {
        "pending_tasks": pending_tasks,
        "selected_task": selected_task,
    }

    return render(
        request,
        "tasks/task_completion_approval.html",
        context
    )

# ==========================================================
# APPROVE COMPLETED TASK
#
# REVIEW
#    ↓
# APPROVE
#    ↓
# COMPLETED
# ==========================================================

@login_required
def approve_completed_task(request, pk):

    task = get_object_or_404(
        Task,
        pk=pk
    )

    if request.method == "POST":

        manager_notes = request.POST.get(
            "manager_notes",
            ""
        ).strip()

        task.approval_status = "Approved"
        task.status = "Completed"
        task.manager_comment = manager_notes
        task.approved_at = timezone.now()

        # Make sure approved tasks show 100%
        if task.progress < 100:
            task.progress = 100

        task.save()

        messages.success(
            request,
            f'Task "{task.title}" has been approved successfully.'
        )

        return redirect("task_completion_approval")

    return redirect("task_completion_approval")
# ==========================================================
# REJECT COMPLETED TASK
#
# REVIEW
#    ↓
# REJECT
#    ↓
# IN PROGRESS
# ==========================================================

@login_required
def reject_completed_task(request, pk):

    # ------------------------------------------------------
    # SECURITY
    #
    # Manager can reject only their own assigned task.
    # ------------------------------------------------------

    task = get_object_or_404(
        Task,
        pk=pk,
        assigned_by=request.user,
        status="Review"
    )

    # ------------------------------------------------------
    # Only POST allowed
    # ------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "task_completion_approval"
        )

    # ------------------------------------------------------
    # Manager feedback
    # ------------------------------------------------------

    manager_comment = request.POST.get(
        "manager_comment",
        ""
    ).strip()

    # ------------------------------------------------------
    # REJECT
    # ------------------------------------------------------

    task.status = "In Progress"

    task.approval_status = "Rejected"

    task.approved_at = None

    if manager_comment:

        task.manager_comment = manager_comment

    task.save()

    messages.warning(
        request,
        f'Task "{task.title}" was rejected and returned to the employee.'
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