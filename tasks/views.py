from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
import csv


from employees.models import Employee
from leave_management.models import LeaveRequest
from timesheets.models import Timesheet


from .models import Task
from .forms import TaskUpdateForm



# =====================================
# EMPLOYEE TASK DASHBOARD
# =====================================

@login_required(login_url="login")
def mytask(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )


    context = {

        "pending_tasks":
            Task.objects.filter(
                employee=employee,
                status="Pending"
            ),


        "progress_tasks":
            Task.objects.filter(
                employee=employee,
                status="In Progress"
            ),


        "review_tasks":
            Task.objects.filter(
                employee=employee,
                status="Review"
            ),


        "completed_tasks":
            Task.objects.filter(
                employee=employee,
                status="Completed"
            ),

    }


    return render(
        request,
        "tasks/MyTask.html",
        context
    )





# =====================================
# UPDATE TASK
# =====================================

@login_required(login_url="login")
def update_task(request, pk):


    employee = get_object_or_404(
        Employee,
        user=request.user
    )


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


            task = form.save(
                commit=False
            )


            # Employee sends for approval
            if task.status == "Review":

                task.approval_status = "Pending"



            # If approved completion
            if task.status == "Completed":

                task.progress = 100



            task.save()



            messages.success(
                request,
                "Task updated successfully."
            )


            return redirect(
                "mytask"
            )



    else:


        form = TaskUpdateForm(
            instance=task
        )



    return render(
        request,
        "tasks/update_task.html",
        {
            "form":form,
            "task":task
        }
    )





# =====================================
# EXPORT TASKS
# =====================================

@login_required(login_url="login")
def export(request):


    employee = get_object_or_404(
        Employee,
        user=request.user
    )


    employee_tasks = Task.objects.filter(
        employee=employee
    )



    response = HttpResponse(
        content_type="text/csv"
    )


    response["Content-Disposition"] = (
        'attachment; filename="MyTasks.csv"'
    )



    writer = csv.writer(response)



    writer.writerow(
        [
            "Task",
            "Project",
            "Priority",
            "Status",
            "Progress",
            "Approval Status",
            "Due Date",
        ]
    )



    for task in employee_tasks:


        writer.writerow(
            [
                task.title,
                task.project,
                task.priority,
                task.status,
                task.progress,
                task.approval_status,
                task.due_date,
            ]
        )



    return response






# =====================================
# APPROVAL DASHBOARD
# =====================================

@login_required(login_url="login")
def approval_dashboard(request):


    pending_leave = LeaveRequest.objects.filter(
        status="Pending"
    ).count()



    pending_task = Task.objects.filter(
        status="Review",
        approval_status="Pending"
    ).count()



    pending_timesheet = Timesheet.objects.filter(
        status="Pending"
    ).count()



    context = {


        "pending_count":
            pending_leave +
            pending_task +
            pending_timesheet,



        "approved_count":

            LeaveRequest.objects.filter(
                status="Approved"
            ).count()

            +

            Task.objects.filter(
                approval_status="Approved"
            ).count()

            +

            Timesheet.objects.filter(
                status="Approved"
            ).count(),




        "rejected_count":

            LeaveRequest.objects.filter(
                status="Rejected"
            ).count()

            +

            Task.objects.filter(
                approval_status="Rejected"
            ).count()

            +

            Timesheet.objects.filter(
                status="Rejected"
            ).count(),



        "pending_leave": pending_leave,

        "pending_task": pending_task,

        "pending_timesheet": pending_timesheet,


    }



    return render(
        request,
        "tasks/approval.html",
        context
    )







# =====================================
# ALL TASK APPROVAL
# =====================================

@login_required(login_url="login")
def task_approval(request):


    all_tasks = Task.objects.select_related(
        "employee",
        "project"
    ).order_by(
        "-created_at"
    )



    return render(
        request,
        "tasks/task_approval.html",
        {
            "all_tasks":all_tasks
        }
    )







# =====================================
# TASK COMPLETION APPROVAL
# =====================================

@login_required(login_url="login")
def task_completion_approval(request):

    # Get all tasks waiting for manager approval
    pending_tasks = Task.objects.filter(
        status="Review",
        approval_status="Pending"
    ).select_related(
        "employee",
        "project"
    ).order_by("-created_at")

    # Selected task (when clicking View Details)
    selected_task = None

    task_id = request.GET.get("task")

    if task_id:
        selected_task = get_object_or_404(
            Task,
            pk=task_id,
            status="Review",
            approval_status="Pending"
        )

    return render(
        request,
        "tasks/task_completion_approval.html",
        {
            "pending_tasks": pending_tasks,
            "selected_task": selected_task,
        }
    )
# =====================================
# APPROVE TASK
# =====================================

# =====================================
# APPROVE TASK
# =====================================

@login_required(login_url="login")
def approve_completed_task(request, pk):

    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":

        task.status = "Completed"
        task.progress = 100
        task.approval_status = "Approved"
        task.approved_at = timezone.now()

        task.manager_comment = request.POST.get(
            "manager_notes",
            ""
        )

        task.save()

        messages.success(
            request,
            "Task approved successfully."
        )

    return redirect("task_completion_approval")

# =====================================
# REJECT TASK
# =====================================

@login_required(login_url="login")
def reject_completed_task(request, pk):

    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":

        task.status = "In Progress"
        task.progress = 90
        task.approval_status = "Rejected"

        task.manager_comment = request.POST.get(
            "manager_notes",
            ""
        )

        task.save()

        messages.warning(
            request,
            "Task returned to employee."
        )

    return redirect("task_completion_approval")

# =====================================
# TIMESHEET APPROVAL
# =====================================

@login_required(login_url="login")
def timesheet_approval(request):

    # Pending timesheets
    timesheets = Timesheet.objects.filter(
        status="Pending"
    ).select_related(
        "employee",
        "employee__user"
    ).order_by(
        "-work_date"
    )


    # Selected timesheet when View Details clicked
    selected_sheet = None

    sheet_id = request.GET.get("sheet")


    if sheet_id:

        selected_sheet = get_object_or_404(
            Timesheet,
            id=sheet_id
        )


    context = {

        "timesheets": timesheets,

        "selected_sheet": selected_sheet,

    }


    return render(
        request,
        "tasks/timesheet_approval.html",
        context
    )

# =====================================
# APPROVE TIMESHEET
# =====================================

@login_required(login_url="login")
def approve_timesheet(request, pk):

    sheet = get_object_or_404(
        Timesheet,
        id=pk
    )

    if request.method == "POST":

        sheet.status = "Approved"
        sheet.save()

        messages.success(
            request,
            "Timesheet approved successfully."
        )


    return redirect(
        "timesheet_approval"
    )



# =====================================
# REJECT TIMESHEET
# =====================================

@login_required(login_url="login")
def reject_timesheet(request, pk):

    sheet = get_object_or_404(
        Timesheet,
        id=pk
    )


    if request.method == "POST":

        sheet.status = "Rejected"

        sheet.manager_comment = request.POST.get(
            "comment",
            ""
        )

        sheet.save()


        messages.warning(
            request,
            "Timesheet rejected."
        )


    return redirect(
        "timesheet_approval"
    )