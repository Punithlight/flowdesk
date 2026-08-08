from datetime import datetime, timedelta
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone

from employees.models import Employee


class Timesheet(models.Model):

    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="timesheets"
    )

    work_date = models.DateField(
        default=timezone.now
    )

    total_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    total_break = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Draft"
    )

    manager_comment = models.TextField(
        blank=True
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def update_totals(self):
        totals = self.entries.aggregate(
            total_hours=Sum("hours"),
            total_break=Sum("break_minutes")
        )

        self.total_hours = totals["total_hours"] or Decimal("0.00")
        self.total_break = totals["total_break"] or 0

        self.save(
            update_fields=[
                "total_hours",
                "total_break",
                "updated_at",
            ]
        )

    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.work_date}"


class TimesheetEntry(models.Model):

    timesheet = models.ForeignKey(
        Timesheet,
        on_delete=models.CASCADE,
        related_name="entries"
    )

    task = models.CharField(
        max_length=200
    )

    clock_in = models.TimeField()

    clock_out = models.TimeField()

    break_minutes = models.PositiveIntegerField(
        default=0
    )

    hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        start = datetime.combine(
            timezone.now().date(),
            self.clock_in
        )

        end = datetime.combine(
            timezone.now().date(),
            self.clock_out
        )

        duration = end - start

        duration -= timedelta(
            minutes=self.break_minutes
        )

        if duration.total_seconds() < 0:
            duration = timedelta(0)

        total_hours = round(
            duration.total_seconds() / 3600,
            2
        )

        self.hours = Decimal(str(total_hours))

        super().save(*args, **kwargs)

        self.timesheet.update_totals()

    def delete(self, *args, **kwargs):
        timesheet = self.timesheet
        super().delete(*args, **kwargs)
        timesheet.update_totals()

    def __str__(self):
        return self.task