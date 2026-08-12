from django.shortcuts import render

# Create your views here.

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from employees.models import Employee
from tasks.models import Task


@login_required(login_url="login")
def teamlead_profile(request):
    employee = get_object_or_404(
        Employee,
        user=request.user,
        role="Team Lead"
    )

    return render(
        request,
        "teamlprofile/profile.html",
        {"employee": employee}
    )


@login_required(login_url="login")
def teamlead_employees(request):
    employee = Employee.objects.filter(user=request.user).first()
    total_members = Employee.objects.count()
    return render(
        request,
        "teamlprofile/employee.html",
        {
            "employee": employee,
            "total_members": total_members,
        }
    )


@login_required(login_url="login")
def task_management(request):
    employees = Employee.objects.select_related("user").all()
    today = timezone.now().date()

    if request.method == "POST":
        # ── Delete task ──
        delete_task_id = request.POST.get("delete_task_id")
        if delete_task_id:
            Task.objects.filter(id=delete_task_id).delete()
            return redirect("task_management")

        # ── Status update ──
        update_task_id = request.POST.get("update_task_id")
        if update_task_id:
            try:
                task = Task.objects.get(id=update_task_id)
                task.status = request.POST.get("status", task.status)
                task.save()
            except Task.DoesNotExist:
                pass
            return redirect("task_management")

        # ── Add new task ──
        employee_id = request.POST.get("employee_id")
        title = request.POST.get("title", "").strip()
        due_date = request.POST.get("due_date")
        attachment = request.FILES.get("attachment")

        if title and due_date and employee_id:
            try:
                employee = Employee.objects.get(id=employee_id)
                Task.objects.create(
                    employee=employee,
                    assigned_by=request.user,
                    title=title,
                    due_date=due_date,
                    status="Pending",
                    attachment=attachment,
                )
            except Employee.DoesNotExist:
                pass
        return redirect("task_management")

    # Build summary per employee
    summary = []
    for emp in employees:
        emp_tasks = Task.objects.filter(employee=emp)
        summary.append({
            "name": emp.user.get_full_name() or emp.user.username,
            "assigned": emp_tasks.count(),
            "in_progress": emp_tasks.filter(status="In Progress").count(),
            "completed": emp_tasks.filter(status="Completed").count(),
            "overdue": emp_tasks.exclude(status="Completed").filter(due_date__lt=today).count(),
        })

    all_tasks = Task.objects.select_related("employee__user").order_by("-created_at")
    for task in all_tasks:
        task.is_overdue = (
            task.due_date < today and task.status != "Completed"
        )

    return render(
        request,
        "teamlprofile/taskmanagement.html",
        {
            "employees": employees,
            "summary": summary,
            "tasks": all_tasks,
        }
    )

