from django.db import models
from employees.models import Employee


class EmployeeAsset(models.Model):

    STATUS_CHOICES = [
        ("Assigned", "Assigned"),
        ("Available", "Available"),
        ("Returned", "Returned"),
        ("Damaged", "Damaged"),
    ]

    ASSET_CHOICES = [
        ("Laptop", "Laptop"),
        ("Monitor", "Monitor"),
        ("Keyboard & Mouse", "Keyboard & Mouse"),
        ("Headset", "Headset"),
        ("ID Card", "ID Card"),
        ("Access Card", "Access Card"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="assets"
    )

    asset_name = models.CharField(max_length=100, choices=ASSET_CHOICES)

    asset_id = models.CharField(max_length=50, unique=True)

    device_name = models.CharField(max_length=200)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Assigned"
    )

    assigned_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.user.username} - {self.asset_name}"