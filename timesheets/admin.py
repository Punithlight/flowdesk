from django.contrib import admin
from .models import Timesheet, TimesheetEntry


class TimesheetEntryInline(admin.TabularInline):
    model = TimesheetEntry
    extra = 1


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "work_date",
        "total_hours",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "work_date",
    )

    search_fields = (
        "employee__user__first_name",
        "employee__user__last_name",
    )

    inlines = [
        TimesheetEntryInline,
    ]


@admin.register(TimesheetEntry)
class TimesheetEntryAdmin(admin.ModelAdmin):

    list_display = (
        "timesheet",
        "task",
        "clock_in",
        "clock_out",
        "hours",
    )

    list_filter = (
        "clock_in",
        "clock_out",
    )

    search_fields = (
        "task",
    )