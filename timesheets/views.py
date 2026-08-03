from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum

from employees.models import Employee
from .models import Timesheet, TimesheetEntry


@login_required
def employee_timesheet(request):
    employee = get_object_or_404(Employee, user=request.user)

    today = timezone.localdate()

    timesheet, created = Timesheet.objects.get_or_create(
        employee=employee,
        work_date=today
    )

    entries = TimesheetEntry.objects.filter(timesheet=timesheet)

    total_hours = entries.aggregate(total=Sum("hours"))["total"] or 0
    total_break = entries.aggregate(total=Sum("break_minutes"))["total"] or 0

    timesheet.total_hours = total_hours
    timesheet.total_break = total_break
    timesheet.save()

    context = {
        "employee": employee,
        "timesheet": timesheet,
        "entries": entries,
        "today": today,
    }

    return render(request, "timesheets/timesheet.html", context)


@login_required
def submit_timesheet(request, pk):
    timesheet = get_object_or_404(Timesheet, id=pk)

    timesheet.status = "Pending"
    timesheet.submitted_at = timezone.now()
    timesheet.save()

    return redirect("employee_timesheet")


@login_required
def manager_timesheets(request):
    pending_timesheets = Timesheet.objects.filter(
        status="Pending"
    ).order_by("-submitted_at")

    context = {
        "timesheets": pending_timesheets,
    }

    return render(
        request,
        "tasks/timesheet-approval.html",
        context,
    )


@login_required
def approve_timesheet(request, pk):
    timesheet = get_object_or_404(Timesheet, id=pk)

    timesheet.status = "Approved"
    timesheet.save()

    return redirect("manager_timesheets")


@login_required
def reject_timesheet(request, pk):
    timesheet = get_object_or_404(Timesheet, id=pk)

    if request.method == "POST":
        timesheet.status = "Rejected"
        timesheet.manager_comment = request.POST.get("comment", "")
        timesheet.save()

    return redirect("manager_timesheets")