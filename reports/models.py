from django.db import models
from employees.models import Employee


class Report(models.Model):

    REPORT_TYPE_CHOICES = [
        ("employee", "Employee Report"),
        ("manager", "Manager / Team Lead Report"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("sent", "Sent"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="reports"
    )

    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        default="employee"
    )

    department = models.CharField(
        max_length=100,
        blank=True
    )

    title = models.CharField(
        max_length=200
    )

    report_text = models.TextField()

    attachment = models.FileField(
        upload_to="reports/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    submitted_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.title} - {self.employee.user.get_full_name()}"

    @property
    def employee_name(self):
        return self.employee.user.get_full_name()

    @property
    def employee_role(self):
        return self.employee.role