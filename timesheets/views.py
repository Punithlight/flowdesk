from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages

from employees.models import Employee
from .models import Timesheet, TimesheetEntry



@login_required
def employee_timesheet(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )


    today = timezone.localdate()


    timesheet, created = Timesheet.objects.get_or_create(
        employee=employee,
        work_date=today
    )


    entries = TimesheetEntry.objects.filter(
        timesheet=timesheet
    )


    totals = entries.aggregate(
        total_hours=Sum("hours"),
        total_break=Sum("break_minutes")
    )


    timesheet.total_hours = totals["total_hours"] or 0

    timesheet.total_break = totals["total_break"] or 0

    timesheet.save()



    context = {

        "employee": employee,

        "timesheet": timesheet,

        "entries": entries,

        "today": today,

    }


    return render(
        request,
        "timesheets/timesheet.html",
        context
    )







@login_required
def submit_timesheet(request, pk):

    if request.method != "POST":
        return redirect("employee_timesheet")


    employee = get_object_or_404(
        Employee,
        user=request.user
    )


    timesheet = get_object_or_404(
        Timesheet,
        pk=pk,
        employee=employee
    )


    timesheet.status = "Pending"
    timesheet.submitted_at = timezone.now()

    timesheet.save()


    messages.success(
        request,
        "Timesheet submitted successfully. Waiting for manager approval."
    )


    return redirect(
        "employee_dashboard"
    )








@login_required
def manager_timesheets(request):

    timesheets = (
        Timesheet.objects
        .select_related("employee", "employee__user")
        .order_by("-work_date")
    )

    context = {
        "timesheets": timesheets
    }

    return render(
        request,
        "tasks/timesheet_approval.html",
        context
    )






@login_required
def approve_timesheet(request, pk):


    if request.method != "POST":

        return redirect(
            "manager_timesheets"
        )



    timesheet = get_object_or_404(
        Timesheet,
        id=pk
    )



    timesheet.status = "Approved"

    timesheet.save()



    messages.success(
        request,
        "Timesheet approved successfully."
    )


    return redirect(
        "timesheet_approval"
    )








@login_required
def reject_timesheet(request, pk):


    if request.method != "POST":

        return redirect(
            "manager_timesheets"
        )



    timesheet = get_object_or_404(
        Timesheet,
        id=pk
    )


    timesheet.status = "Rejected"


    timesheet.manager_comment = request.POST.get(
        "comment",
        ""
    )


    timesheet.save()



    messages.success(
        request,
        "Timesheet rejected."
    )


    return redirect(
        "manager_timesheets"
    )


