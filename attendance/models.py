from django.db import models
from employees.models import Employee


class Attendance(models.Model):

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Half Day', 'Half Day'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    # Attendance Date
    date = models.DateField(auto_now_add=True)

    # Check In / Check Out
    check_in = models.DateTimeField(
        null=True,
        blank=True
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True
    )

    # Break Details
    break_start = models.DateTimeField(
        null=True,
        blank=True
    )

    break_end = models.DateTimeField(
        null=True,
        blank=True
    )

    is_on_break = models.BooleanField(
        default=False
    )

    total_break_minutes = models.PositiveIntegerField(
        default=0
    )

    # Working Hours
    working_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )

    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )

    # Attendance Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Present'
    )

    # Optional Remarks
    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "attendance"
        ordering = ['-date']
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee} - {self.date}"