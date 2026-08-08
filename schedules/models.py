from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Schedule(models.Model):

    STATUS = (
        ("Upcoming", "Upcoming"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )


    title = models.CharField(
        max_length=200
    )


    description = models.TextField(
        blank=True,
        null=True
    )


    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="manager_schedules"
    )


    participants = models.ManyToManyField(
        User,
        through="ScheduleParticipant",
        related_name="employee_schedules",
        blank=True
    )


    meeting_date = models.DateField(
        db_index=True
    )


    start_time = models.TimeField()


    end_time = models.TimeField()


    venue = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Upcoming"
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )



    class Meta:

        ordering = [
            "meeting_date",
            "start_time"
        ]

        verbose_name = "Schedule"

        verbose_name_plural = "Schedules"



    def __str__(self):

        return f"{self.title} - {self.meeting_date}"

class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=50,
        default="General"
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.title



class ScheduleParticipant(models.Model):

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name="participant_links"
    )


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="schedule_participant_links"
    )



    class Meta:

        db_table = "schedules_scheduleparticipant"


        unique_together = (
            "schedule",
            "user",
        )



    def __str__(self):

        return f"{self.schedule.title} - {self.user.username}"