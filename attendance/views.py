from datetime import timedelta

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from employees.models import Employee
from .models import Attendance


def attendance_dashboard(request):
    employee = get_object_or_404(Employee, user=request.user)

    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=timezone.localdate(),
        defaults={"status": "Present"},
    )

    history = Attendance.objects.filter(employee=employee).order_by("-date")

    monthly_records = Attendance.objects.filter(
        employee=employee,
        date__month=timezone.localdate().month,
        date__year=timezone.localdate().year,
    )

    monthly_working_hours = (
        monthly_records.aggregate(Sum("working_hours"))["working_hours__sum"] or 0
    )

    present_days = monthly_records.filter(status="Present").count()
    absent_days = monthly_records.filter(status="Absent").count()

    overtime_hours = (
        monthly_records.aggregate(Sum("overtime_hours"))["overtime_hours__sum"] or 0
    )

    context = {
        "attendance": attendance,
        "history": history,
        "monthly_working_hours": monthly_working_hours,
        "present_days": present_days,
        "absent_days": absent_days,
        "overtime_hours": overtime_hours,
    }

    return render(request, "attendance/attendance.html", context)


def check_in(request):
    employee = get_object_or_404(Employee, user=request.user)

    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=timezone.localdate(),
        defaults={"status": "Present"},
    )

    if attendance.check_in:
        messages.warning(request, "Already checked in.")
    else:
        attendance.check_in = timezone.now()  # Save in UTC correctly
        attendance.status = "Present"
        attendance.save()

        messages.success(request, "Checked in successfully.")

    return redirect("attendance_dashboard")


def start_break(request):
    employee = get_object_or_404(Employee, user=request.user)

    attendance = get_object_or_404(
        Attendance,
        employee=employee,
        date=timezone.localdate(),
    )

    if attendance.check_out:
        messages.warning(request, "You have already checked out.")
    elif not attendance.check_in:
        messages.warning(request, "Please check in before starting a break.")
    elif attendance.is_on_break:
        messages.warning(request, "Break already started.")
    else:
        attendance.break_start = timezone.now()
        attendance.is_on_break = True
        attendance.save()

        messages.success(request, "Break started.")

    return redirect("attendance_dashboard")


def end_break(request):
    employee = get_object_or_404(Employee, user=request.user)

    attendance = get_object_or_404(
        Attendance,
        employee=employee,
        date=timezone.localdate(),
    )

    if attendance.is_on_break and attendance.break_start:
        break_end = timezone.now()

        minutes = int(
            (break_end - attendance.break_start).total_seconds() / 60
        )

        attendance.total_break_minutes += minutes
        attendance.break_end = break_end
        attendance.is_on_break = False
        attendance.save()

        messages.success(request, "Break ended.")
    else:
        messages.warning(request, "No active break.")

    return redirect("attendance_dashboard")


def check_out(request):
    employee = get_object_or_404(Employee, user=request.user)

    attendance = get_object_or_404(
        Attendance,
        employee=employee,
        date=timezone.localdate(),
    )

    if attendance.check_out:
        messages.warning(request, "Already checked out.")

    elif not attendance.check_in:
        messages.warning(request, "Please check in before checking out.")

    elif attendance.is_on_break:
        messages.warning(request, "Please end your break before checking out.")

    else:
        attendance.check_out = timezone.now()

        worked = (
            attendance.check_out - attendance.check_in
        ) - timedelta(minutes=attendance.total_break_minutes)

        hours = max(worked.total_seconds() / 3600, 0)

        attendance.working_hours = round(hours, 2)
        attendance.overtime_hours = round(max(hours - 8, 0), 2)
        attendance.save()

        messages.success(request, "Checked out successfully.")

    return redirect("attendance_dashboard")