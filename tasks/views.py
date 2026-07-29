from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv

from employees.models import Employee
from .models import tasks
from .forms import TaskUpdateForm


@login_required(login_url="login")
def mytask(request):

    employee = Employee.objects.get(user=request.user)

    pending_tasks = tasks.objects.filter(
        employee=employee,
        status="Pending"
    )

    progress_tasks = tasks.objects.filter(
        employee=employee,
        status="In Progress"
    )

    review_tasks = tasks.objects.filter(
        employee=employee,
        status="Review"
    )

    completed_tasks = tasks.objects.filter(
        employee=employee,
        status="Completed"
    )

    context = {
        "pending_tasks": pending_tasks,
        "progress_tasks": progress_tasks,
        "review_tasks": review_tasks,
        "completed_tasks": completed_tasks,
    }

    return render(request, "tasks/MyTask.html", context)


@login_required(login_url="login")
def update_task(request, pk):

    employee = Employee.objects.get(user=request.user)

    task = get_object_or_404(
        tasks,
        id=pk,
        employee=employee
    )

    if request.method == "POST":

        form = TaskUpdateForm(
            request.POST,
            request.FILES,
            instance=task
        )

        if form.is_valid():

            task = form.save(commit=False)

            if task.status == "Completed":
                task.progress = 100

            task.save()

            return redirect("mytask")

    else:

        form = TaskUpdateForm(instance=task)

    return render(
        request,
        "tasks/update_task.html",
        {
            "form": form,
            "task": task
        }
    )


# ===========================
# EXPORT TASKS
# ===========================

@login_required(login_url="login")
def export(request):

    employee = Employee.objects.get(user=request.user)

    employee_tasks = tasks.objects.filter(employee=employee)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="MyTasks.csv"'

    writer = csv.writer(response)

    # Header
    writer.writerow([
        "Task Title",
        "Project",
        "Description",
        "Priority",
        "Status",
        "Progress (%)",
        "Due Date",
        "Start Time",
        "End Time",
        "Employee Comment",
        "Created At",
    ])

    # Data
    for task in employee_tasks:
        writer.writerow([
            task.title,
            str(task.project),      # Uses Project __str__()
            task.description,
            task.priority,
            task.status,
            task.progress,
            task.due_date,
            task.start_time,
            task.end_time,
            task.employee_comment,
            task.created_at,
        ])

    return response