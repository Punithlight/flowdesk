from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from employees.models import Employee
from projects.models import Project
from tasks.models import Task
from attendance.models import Attendance
from leave_management.models import LeaveRequest
from assets.models import EmployeeAsset
from notifications.models import Notification


# ==========================================================
# Employee Dashboard
# ==========================================================
@login_required(login_url="login")
def employee_dashboard(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    # =====================================================
    # Employee Tasks
    # =====================================================

    my_tasks = Task.objects.filter(
        employee=employee
    )

    total_tasks = my_tasks.count()

    pending_tasks = my_tasks.filter(
        status="Pending"
    ).count()

    inprogress_tasks = my_tasks.filter(
        status="In Progress"
    ).count()

    review_tasks = my_tasks.filter(
        status="Review"
    ).count()

    completed_tasks = my_tasks.filter(
        status="Completed"
    ).count()

    upcoming_tasks = my_tasks.order_by(
        "due_date"
    )[:5]

    # Today's Schedule
    today_schedule = my_tasks.filter(
        due_date=timezone.now().date()
    ).order_by("start_time")

    # =====================================================
    # Employee Projects
    # =====================================================

   # =====================================================
# Employee Projects
# =====================================================

    my_projects = Project.objects.filter(
        employee=request.user
    )

    total_projects = my_projects.count()

    completed_projects = my_projects.filter(
        status="completed"
    ).count()

    inprogress_projects = my_projects.filter(
        status="in_progress"
    ).count()

    pending_projects = my_projects.filter(
        status="pending"
    ).count()

    # =====================================================
    # Attendance
    # =====================================================

    attendance_count = Attendance.objects.filter(
        employee=employee
    ).count()

    # =====================================================
    # Leave
    # =====================================================

    TOTAL_ANNUAL_LEAVE = 20

    leave_requests = LeaveRequest.objects.filter(
        employee=request.user
    )

    pending_leave = leave_requests.filter(
        status="Pending"
    ).count()

    approved_leave = leave_requests.filter(
        status="Approved"
    )

    approved_this_month = approved_leave.filter(
        from_date__month=timezone.now().month,
        from_date__year=timezone.now().year
    ).count()

    used_leave_days = 0

    for leave in approved_leave:
        used_leave_days += (leave.to_date - leave.from_date).days + 1

    leave_balance = TOTAL_ANNUAL_LEAVE - used_leave_days

    if leave_balance < 0:
        leave_balance = 0
    # =====================================================
    # Assets
    # =====================================================

    total_assets = EmployeeAsset.objects.filter(
        employee=employee
    ).count()

    # =====================================================
    # Notifications
    # =====================================================
    
    latest_notifications = Notification.objects.filter(
        employee=employee
    ).order_by("-created_at")[:5]

    unread_notifications = Notification.objects.filter(
        employee=employee,
        is_read=False
    ).count()

    context = {

        "employee": employee,

        "today": timezone.now(),

        # Tasks
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "inprogress_tasks": inprogress_tasks,
        "review_tasks": review_tasks,
        "completed_tasks": completed_tasks,
        "today_tasks": upcoming_tasks,
        "today_schedule": today_schedule,

        "pending_count": pending_tasks,
        "inprogress_count": inprogress_tasks,
        "review_count": review_tasks,
        "completed_count": completed_tasks,
        
        # Projects
        "total_projects": total_projects,
        "my_projects": my_projects,

        "completed_projects": completed_projects,
        "inprogress_projects": inprogress_projects,
        "pending_projects": pending_projects,
        

       
        # "tasks_completed": tasks_completed,
        # "pending_review": pending_review,
        # "projects_active": projects_active,



        # Attendance
        "attendance": attendance_count,

        # Leave
   
        "pending_leave": pending_leave,
        "approved_this_month": approved_this_month,
        "used_leave_days": used_leave_days,
        "leave_balance": leave_balance,

        # Assets
        "total_assets": total_assets,

        # Notifications
        "notifications": latest_notifications,
        "unread_notifications": unread_notifications,

    }
    # context = {
    #     "tasks_completed": tasks_completed,
    #     "pending_review": pending_review,
    #     "projects_active": projects_active,
    # }

    return render(
        request,
        "dashboard/employee_dashboard.html",
        context
    )


# ==========================================================
# Manager Dashboard
# ==========================================================
@login_required(login_url="login")
def manager_dashboard(request):

    manager = Employee.objects.filter(
        user=request.user
    ).first()

    if manager is None:
        messages.error(
            request,
            "Manager profile not found."
        )
        return redirect("login")

    # =====================================================
    # Projects
    # =====================================================

    total_projects = Project.objects.count()

    inprogress_projects = Project.objects.filter(
        status="In Progress"
    ).count()

    completed_projects = Project.objects.filter(
        status="Completed"
    ).count()

    pending_projects = Project.objects.filter(
        status="Pending"
    ).count()

    # =====================================================
    # Employees
    # =====================================================

    total_employees = Employee.objects.count()

    # =====================================================
    # Tasks
    # =====================================================

    total_tasks = Task.objects.count()

    completed_tasks = Task.objects.filter(
        status="Completed"
    ).count()

    pending_tasks = Task.objects.filter(
        status="Pending"
    ).count()

    inprogress_tasks = Task.objects.filter(
        status="In Progress"
    ).count()

    review_tasks = Task.objects.filter(
        status="Review"
    ).count()

    # =====================================================
    # Leave
    # =====================================================

    pending_leave = LeaveRequest.objects.filter(
        status="Pending"
    ).count()

    # =====================================================
    # Notifications
    # =====================================================
    latest_notifications = Notification.objects.filter(
        employee=manager
    ).order_by("-created_at")[:5]

    unread_notifications = Notification.objects.filter(
        employee=manager,
        is_read=False
    ).count()

    recent_projects = Project.objects.order_by(
        "-id"
    )[:5]

    recent_tasks = Task.objects.order_by(
        "-created_at"
    )[:5]

    context = {

        "manager": manager,

        "today": timezone.now(),

        "total_employees": total_employees,

        "total_projects": total_projects,
        "inprogress_projects": inprogress_projects,
        "completed_projects": completed_projects,
        "pending_projects": pending_projects,

        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "inprogress_tasks": inprogress_tasks,
        "review_tasks": review_tasks,

        "pending_leave": pending_leave,
        
        "notifications": latest_notifications,
        "unread_notifications": unread_notifications,

        "recent_projects": recent_projects,
        "recent_tasks": recent_tasks,

    }

    return render(
        request,
        "dashboard/manager_dashboard.html",
        context
    )


# ==========================================================
# My Tasks
# ==========================================================
@login_required(login_url="login")
def mytask(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    pending_tasks = Task.objects.filter(
        employee=employee,
        status="Pending"
    )

    progress_tasks = Task.objects.filter(
        employee=employee,
        status="In Progress"
    )

    review_tasks = Task.objects.filter(
        employee=employee,
        status="Review"
    )

    completed_tasks = Task.objects.filter(
        employee=employee,
        status="Completed"
    )

    context = {

        "pending_tasks": pending_tasks,
        "progress_tasks": progress_tasks,
        "review_tasks": review_tasks,
        "completed_tasks": completed_tasks,

    }

    return render(
        request,
        "tasks/mytask.html",
        context
    )


# ==========================================================
# Admin Dashboard
# ==========================================================
@login_required(login_url="login")
def admin_dashboard(request):

    return render(
        request,
        "dashboard/admin_dashboard.html"
    )