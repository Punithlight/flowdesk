from django.db import models
from employees.models import Employee


class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ("Announcement", "Announcement"),
        ("Task", "Task"),
        ("Meeting", "Meeting"),
        ("Alert", "Alert"),
        ("Leave", "Leave"),
        ("Birthday", "Birthday"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title