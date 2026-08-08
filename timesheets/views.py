from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from employees.models import Employee
from .models import Timesheet, TimesheetEntry
from .forms import TimesheetEntryForm

from datetime import datetime

@login_required
def employee_timesheet(request):

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    today = timezone.localdate()

    timesheet, created = Timesheet.objects.get_or_create(
        employee=employee,
        work_date=today,
        defaults={
            "status": "Draft"
        }
    )

    entries = (
        timesheet.entries
        .all()
        .order_by("created_at")
    )

    form = TimesheetEntryForm()


    context = {
        "employee": employee,
        "timesheet": timesheet,
        "entries": entries,
        "form": form,
    }


    return render(
        request,
        "timesheets/timesheet.html",
        context
    )


# =====================================
# Add Timesheet Entry
# =====================================

@login_required
def add_entry(request, pk):

    timesheet = get_object_or_404(
        Timesheet,
        id=pk
    )


    if request.method == "POST":

        form = TimesheetEntryForm(
            request.POST
        )


        if form.is_valid():

            entry = form.save(
                commit=False
            )

            entry.timesheet = timesheet


            start = datetime.combine(
                timesheet.work_date,
                entry.clock_in
            )

            end = datetime.combine(
                timesheet.work_date,
                entry.clock_out
            )


            hours = (
                end - start
            ).total_seconds() / 3600


            hours -= (
                entry.break_minutes / 60
            )


            entry.hours = max(
                round(hours, 2),
                0
            )


            entry.save()


            messages.success(
                request,
                "Timesheet entry added successfully."
            )


            return redirect(
                "employee_timesheet"
            )


    else:

        form = TimesheetEntryForm()



    return render(
        request,
        "timesheets/add_entry.html",
        {
            "form": form,
            "timesheet": timesheet
        }
    )



# =====================================
# Edit Timesheet Entry
# =====================================

@login_required
def edit_entry(request, pk):

    entry = get_object_or_404(
        TimesheetEntry,
        id=pk
    )


    if request.method == "POST":

        form = TimesheetEntryForm(
            request.POST,
            instance=entry
        )


        if form.is_valid():

            entry = form.save(
                commit=False
            )


            start = datetime.combine(
                entry.timesheet.work_date,
                entry.clock_in
            )


            end = datetime.combine(
                entry.timesheet.work_date,
                entry.clock_out
            )


            hours = (
                end-start
            ).total_seconds()/3600


            hours -= (
                entry.break_minutes/60
            )


            entry.hours = max(
                round(hours,2),
                0
            )


            entry.save()


            messages.success(
                request,
                "Timesheet entry updated successfully."
            )


            return redirect(
                "employee_timesheet"
            )


    else:

        form = TimesheetEntryForm(
            instance=entry
        )



    return render(
        request,
        "timesheets/edit_entry.html",
        {
            "form": form,
            "entry": entry
        }
    )



# =====================================
# Delete Timesheet Entry
# =====================================

@login_required
def delete_entry(request, pk):

    entry = get_object_or_404(
        TimesheetEntry,
        id=pk
    )


    entry.delete()


    messages.success(
        request,
        "Timesheet entry deleted successfully."
    )


    return redirect(
        "employee_timesheet"
    )



# =====================================
# Submit Timesheet
# =====================================

@login_required
def submit_timesheet(request, pk):

    print("========== submit_timesheet called ==========")

    print("Method:", request.method)
    print("PK:", pk)

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    print("Employee:", employee)

    timesheet = get_object_or_404(
        Timesheet,
        id=pk,
        employee=employee
    )

    print("Before:", timesheet.status)

    timesheet.status = "Pending"
    timesheet.submitted_at = timezone.now()
    timesheet.save()

    timesheet.refresh_from_db()

    print("After:", timesheet.status)

    messages.success(
        request,
        "Timesheet submitted successfully."
    )

    return redirect("employee_dashboard")


# =====================================
# Manager Timesheet Approval Page
# =====================================

@login_required
def manager_timesheets(request):

    timesheets = (
        Timesheet.objects
        .select_related("employee", "employee__user")
        .prefetch_related("entries")
        .filter(status="Pending")
        .order_by("-work_date")
    )

    selected_sheet = None

    sheet_id = request.GET.get("sheet")

    if sheet_id:
        selected_sheet = get_object_or_404(
            Timesheet.objects.select_related(
                "employee",
                "employee__user"
            ).prefetch_related("entries"),
            pk=sheet_id
        )

    return render(
        request,
        "tasks/timesheet_approval.html",
        {
            "timesheets": timesheets,
            "selected_sheet": selected_sheet,
        }
    )
# =====================================
# Approve Timesheet
# =====================================

@login_required
def approve_timesheet(request, pk):

    if request.method != "POST":

        return redirect(
            "timesheet_approval"
        )


    timesheet = get_object_or_404(
        Timesheet,
        id=pk
    )


    timesheet.status = "Approved"

    timesheet.manager_comment = ""

    timesheet.save()



    messages.success(
        request,
        "Timesheet approved successfully."
    )


    return redirect(
        "timesheet_approval"
    )



# =====================================
# Reject Timesheet
# =====================================

@login_required
def reject_timesheet(request, pk):

    if request.method != "POST":

        return redirect(
            "timesheet_approval"
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
        "timesheet_approval"
    )