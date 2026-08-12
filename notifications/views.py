from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from employees.models import Employee
from .models import Notification


# ==========================================================
# Employee Notification Page
# ==========================================================

@login_required(login_url="login")
def notification_list(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    notifications = Notification.objects.filter(
        employee=employee
    ).order_by("-created_at")

    # Mark all unread notifications as read
    notifications.filter(is_read=False).update(is_read=True)

    unread_count = Notification.objects.filter(
        employee=employee,
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


# ==========================================================
# Manager Notification Page
# ==========================================================

@login_required(login_url="login")
def manager_notifications(request):

    employees = Employee.objects.select_related(
        "user"
    ).order_by("user__first_name")

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


# ==========================================================
# Mark Notification as Read
# ==========================================================

@login_required(login_url="login")
def mark_read(request, id):

    print("MARK READ CLICKED:", id)

    notification = get_object_or_404(
        Notification,
        id=id
    )

    notification.is_read = True
    notification.save()

    return redirect("notifications:list")


# ==========================================================
# Team Lead Notification Page
# ==========================================================

@login_required(login_url="login")
def team_lead_notifications(request):

    employees = Employee.objects.select_related(
        "user"
    ).order_by("user__first_name")

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

        return redirect(
            "notifications:teamlead_notifications"
        )

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
        "notifications/Team_lead_notification.html",
        context
    )


# ==========================================================
# TEAM LEAD BELL - UNREAD NOTIFICATIONS
# ==========================================================

@login_required(login_url="login")
def teamlead_unread_notifications(request):

    # Get the Employee record belonging to
    # the currently logged-in Team Lead
    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    # Get unread notifications for this Team Lead
    unread_notifications = Notification.objects.filter(
        employee=employee,
        is_read=False
    ).order_by("-created_at")

    # Count unread notifications
    unread_count = unread_notifications.count()

    # Send latest unread notifications to JavaScript
    notifications = []

    for notification in unread_notifications[:5]:

        notifications.append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "is_read": notification.is_read,
            "created_at": notification.created_at.strftime(
                "%d %b %Y, %I:%M %p"
            ),
        })

    return JsonResponse({
        "unread_count": unread_count,
        "notifications": notifications,
    })