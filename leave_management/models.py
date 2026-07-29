from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class LeaveRequest(models.Model):

    LEAVE_TYPE_CHOICES = [
        ('Casual Leave', 'Casual Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Personal Leave', 'Personal Leave'),
        ('Annual Leave', 'Annual Leave'),
        ('Festival Leave', 'Festival Leave'),
    ]


    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('In Review', 'In Review'),
    ]


    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )


    leave_type = models.CharField(
        max_length=50,
        choices=LEAVE_TYPE_CHOICES
    )


    from_date = models.DateField()


    to_date = models.DateField()


    total_days = models.PositiveIntegerField(
        default=1
    )


    description = models.TextField(
        blank=True,
        null=True
    )


    attachment = models.FileField(
        upload_to="leave_attachments/",
        blank=True,
        null=True
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )


    applied_on = models.DateTimeField(
        default=timezone.now
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    def clean(self):
        """
        Validate leave dates
        """
        if self.from_date and self.to_date:

            if self.to_date < self.from_date:
                raise ValidationError(
                    "To date cannot be before From date."
                )


    def save(self, *args, **kwargs):

        if self.from_date and self.to_date:
            self.total_days = (
                self.to_date - self.from_date
            ).days + 1

        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.status})"


    class Meta:

        ordering = [
            '-applied_on'
        ]

        verbose_name = "Leave Request"

        verbose_name_plural = "Leave Requests"