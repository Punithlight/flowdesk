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

from django.db.models import Q

# ==========================================================
# Employee Dashboard
# ==========================================================

@login_required(login_url="login")
def employee_dashboard(request):

    print("========== EMPLOYEE DASHBOARD ==========")
    print("Logged-in User:", request.user)
    print("Username:", request.user.username)

    # =====================================================
    # GET LOGGED-IN EMPLOYEE ONLY
    # =====================================================

    employee = Employee.objects.filter(
        user=request.user,
        role__iexact="Employee"
    ).select_related("user").first()

    # =====================================================
    # PREVENT TEAM LEAD / MANAGER FROM USING EMPLOYEE DASHBOARD
    # =====================================================

    if employee is None:

        current_employee = Employee.objects.filter(
            user=request.user
        ).select_related("user").first()

        if current_employee:

            role = (current_employee.role or "").strip().lower()

            print("Current Role:", current_employee.role)

            if role == "team lead":
                return redirect("teamlead_dashboard")

            if role == "manager":
                return redirect("manager_dashboard")

            if role in ["admin", "super admin"]:
                return redirect("admin_dashboard")

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect("login")

    print("Employee:", employee)
    print("Employee User:", employee.user)
    print("Employee Role:", employee.role)

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

    today_schedule = my_tasks.filter(
        due_date=timezone.now().date()
    ).order_by(
        "start_time"
    )

    # =====================================================
    # Employee Projects
    # Project.employee --> User
    # =====================================================

    my_projects = Project.objects.filter(
        employee=request.user
    )

    total_projects = my_projects.count()

    completed_projects = my_projects.filter(
        status__iexact="completed"
    ).count()

    inprogress_projects = my_projects.filter(
        status__iexact="in_progress"
    ).count()

    pending_projects = my_projects.filter(
        status__iexact="pending"
    ).count()

    # =====================================================
    # Attendance
    # =====================================================

    attendance_count = Attendance.objects.filter(
        employee=employee
    ).count()

    # =====================================================
    # Leave Management
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

        used_leave_days += (
            leave.to_date - leave.from_date
        ).days + 1

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
    ).order_by(
        "-created_at"
    )[:5]

    unread_notifications = Notification.objects.filter(
        employee=employee,
        is_read=False
    ).count()

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        # =================================================
        # Employee Profile
        # =================================================

        "employee": employee,

        "today": timezone.now(),

        # =================================================
        # Tasks
        # =================================================

        "total_tasks": total_tasks,

        "pending_tasks": pending_tasks,

        "inprogress_tasks": inprogress_tasks,

        "review_tasks": review_tasks,

        "completed_tasks": completed_tasks,

        "today_tasks": upcoming_tasks,

        "today_schedule": today_schedule,

        # =================================================
        # Chart Data
        # =================================================

        "pending_count": pending_tasks,

        "inprogress_count": inprogress_tasks,

        "review_count": review_tasks,

        "completed_count": completed_tasks,

        # =================================================
        # Projects
        # =================================================

        "my_projects": my_projects,

        "total_projects": total_projects,

        "completed_projects": completed_projects,

        "inprogress_projects": inprogress_projects,

        "pending_projects": pending_projects,

        # =================================================
        # Stats
        # =================================================

        "tasks_completed": completed_tasks,

        "pending_review": review_tasks,

        "projects_active": inprogress_projects,

        # =================================================
        # Attendance
        # =================================================

        "attendance": attendance_count,

        # =================================================
        # Leave
        # =================================================

        "pending_leave": pending_leave,

        "approved_this_month": approved_this_month,

        "used_leave_days": used_leave_days,

        "leave_balance": leave_balance,

        # =================================================
        # Assets
        # =================================================

        "total_assets": total_assets,

        # =================================================
        # Notifications
        # =================================================

        "notifications": latest_notifications,

        "unread_notifications": unread_notifications,
    }

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



    total_projects = Project.objects.count()


    inprogress_projects = Project.objects.filter(
        status="in_progress"
    ).count()


    completed_projects = Project.objects.filter(
        status="completed"
    ).count()


    pending_projects = Project.objects.filter(
        status="pending"
    ).count()



    total_employees = Employee.objects.count()



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



    pending_leave = LeaveRequest.objects.filter(
        status="Pending"
    ).count()



    latest_notifications = Notification.objects.filter(
        employee=manager
    ).order_by(
        "-created_at"
    )[:5]



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
# Team Lead Dashboard
# ==========================================================

@login_required(login_url="login")
def teamlead_dashboard(request):

    # ------------------------------------------------------
    # LOGGED-IN TEAM LEAD
    # ------------------------------------------------------

    team_lead = Employee.objects.filter(
        user=request.user,
        role__iexact="Team Lead"
    ).select_related("user").first()

    # ------------------------------------------------------
    # TEAM LEAD PROFILE NOT FOUND
    # ------------------------------------------------------

    if team_lead is None:

        messages.error(
            request,
            "Team Lead profile not found."
        )

        return redirect("login")

    # ------------------------------------------------------
    # PROJECTS
    # ------------------------------------------------------

    projects = Project.objects.all()

    total_projects = projects.count()

    active_projects = projects.filter(
        status="in_progress"
    ).count()

    completed_projects = projects.filter(
        status="completed"
    ).count()

    pending_projects = projects.filter(
        status="pending"
    ).count()

    # ------------------------------------------------------
    # TASKS
    # ------------------------------------------------------

    tasks = Task.objects.all()

    total_tasks = tasks.count()

    pending_tasks = tasks.filter(
        status="Pending"
    ).count()

    inprogress_tasks = tasks.filter(
        status="In Progress"
    ).count()

    review_tasks = tasks.filter(
        status="Review"
    ).count()

    completed_tasks = tasks.filter(
        status="Completed"
    ).count()

    # ------------------------------------------------------
    # CONTEXT
    # ------------------------------------------------------

    context = {

        # Team Lead profile
        "team_lead": team_lead,

        # Keep employee also if your existing HTML uses it
        "employee": team_lead,

        "today": timezone.now(),

        # Projects
        "projects": projects,

        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "pending_projects": pending_projects,

        # Tasks
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "inprogress_tasks": inprogress_tasks,
        "review_tasks": review_tasks,
        "completed_tasks": completed_tasks,
    }

    return render(
        request,
        "dashboard/teamlead_dashboard.html",
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


# ==========================================================
# TEAM LEAD PROJECTS / ASSIGN TASK
# ==========================================================

@login_required
def teamlead_projects(request):

    # Logged-in Team Lead
    teamlead = get_object_or_404(
        Employee,
        user=request.user,
        role="Team Lead"
    )

    # Get all employees
    employees = Employee.objects.filter(
        role__iexact="Employee"
    ).select_related("user")

    # DEBUG
    print("======================================")
    print("TEAMLEAD PROJECTS VIEW CALLED")
    print("TEAM LEAD:", teamlead)
    print("EMPLOYEE COUNT:", employees.count())
    print(
        "EMPLOYEES:",
        list(
            employees.values(
                "id",
                "employee_id",
                "user_id",
                "role"
            )
        )
    )
    print("======================================")

    # Get all projects
    projects = Project.objects.all().order_by("-id")

    total_projects = projects.count()

    active_projects = projects.filter(
        status__iexact="Active"
    ).count()

    completed_projects = projects.filter(
        status__iexact="Completed"
    ).count()

    overdue_projects = projects.filter(
        end_date__lt=timezone.localdate()
    ).exclude(
        status__iexact="Completed"
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
    
    
    