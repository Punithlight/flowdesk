from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "date",
        "check_in",
        "check_out",
        "working_hours",
        "overtime_hours",
        "status",
    )

    list_filter = (
        "status",
        "date",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__employee_id",
    )

    readonly_fields = (
        "date",          # Required: date uses auto_now_add=True
        "created_at",
        "updated_at",
    )

    ordering = (
        "-date",
        "-check_in",
    )

    fieldsets = (
        ("Employee Information", {
            "fields": (
                "employee",
                "date",
                "status",
            )
        }),

        ("Attendance", {
            "fields": (
                "check_in",
                "check_out",
            )
        }),

        ("Break Details", {
            "fields": (
                "break_start",
                "break_end",
                "is_on_break",
                "total_break_minutes",
            )
        }),

        ("Working Hours", {
            "fields": (
                "working_hours",
                "overtime_hours",
            )
        }),

        ("Remarks", {
            "fields": (
                "remarks",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )