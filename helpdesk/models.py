from django.db import models
from employees.models import Employee


class SupportTicket(models.Model):

    TICKET_TYPE = [
        ("Issue", "Issue"),
        ("Feedback", "Feedback"),
        ("Request", "Request"),
    ]

    STATUS = [
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="support_tickets"
    )

    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    subject = models.CharField(max_length=200)

    description = models.TextField()

    ticket_type = models.CharField(
        max_length=20,
        choices=TICKET_TYPE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Open"
    )

    progress = models.PositiveIntegerField(default=5)

    priority = models.CharField(
        max_length=10,
        choices=[
            ("Low", "Low"),
            ("Medium", "Medium"),
            ("High", "High"),
        ],
        default="Medium"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            last_id = SupportTicket.objects.count() + 1001
            self.ticket_number = f"INC-{last_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_number