from django.db import models
from django.conf import settings


class CalendarEvent(models.Model):

    EVENT_TYPES = [
        ("Meeting", "Meeting"),
        ("Holiday", "Holiday"),
        ("Reminder", "Reminder"),
    ]

    title = models.CharField(max_length=200)
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES
    )

    description = models.TextField(blank=True)

    start_date = models.DateField()
    end_date = models.DateField()

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="calendar_events"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date", "start_time"]

    def __str__(self):
        return self.title