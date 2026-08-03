from django.db import models
from django.utils import timezone
from employees.models import Employee
from tasks.models import Task

class Timesheet(models.Model):

    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    work_date = models.DateField(default=timezone.now)

    total_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    total_break = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Draft"
    )

    manager_comment = models.TextField(blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_name} - {self.work_date}"


class TimesheetEntry(models.Model):

    timesheet = models.ForeignKey(
        Timesheet,
        on_delete=models.CASCADE,
        related_name="entries"
    )

    task = models.CharField(max_length=200)

    clock_in = models.TimeField()

    clock_out = models.TimeField()

    break_minutes = models.PositiveIntegerField(default=0)

    hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task