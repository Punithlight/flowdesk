from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from employees.models import Employee
from .models import Notification


# ===========================
# Employee Notification Page
# ===========================

@login_required(login_url="login")
def notification_list(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    notifications = Notification.objects.filter(
        employee=employee
    ).order_by("-created_at")

    unread_count = notifications.filter(
        is_read=False
    ).count()

    announcement_count = notifications.filter(
        notification_type="Announcement"
    ).count()

    task_count = notifications.filter(
        notification_type="Task"
    ).count()

    meeting_count = notifications.filter(
        notification_type="Meeting"
    ).count()

    context = {

        "notifications": notifications,

        "unread_count": unread_count,

        "announcement_count": announcement_count,

        "task_count": task_count,

        "meeting_count": meeting_count,

    }

    return render(
        request,
        "notifications/notification.html",
        context
    )


# ===========================
# Manager Notification Page
# ===========================

@login_required(login_url="login")
def manager_notifications(request):

    employees = Employee.objects.select_related("user").order_by("user__first_name")

    if request.method == "POST":

        employee_id = request.POST.get("employee")
        title = request.POST.get("title")
        message = request.POST.get("message")
        notification_type = request.POST.get("notification_type")

        employee = get_object_or_404(
            Employee,
            id=employee_id
        )

        Notification.objects.create(
            employee=employee,
            title=title,
            message=message,
            notification_type=notification_type
        )

        messages.success(
            request,
            "Notification sent successfully."
        )

        return redirect("manager_notifications")

    history = Notification.objects.select_related(
        "employee"
    ).order_by("-created_at")

    context = {

        "employees": employees,

        "history": history,

        "notification_types": Notification.NOTIFICATION_TYPES,

    }

    return render(
        request,
        "notifications/manager_notification.html",
        context
    )