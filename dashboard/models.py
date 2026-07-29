from django.db import models


class Dashboard(models.Model):
    welcome_title = models.CharField(max_length=200)
    welcome_message = models.TextField()

    today_tasks = models.PositiveIntegerField(default=0)
    active_projects = models.PositiveIntegerField(default=0)
    pending_reviews = models.PositiveIntegerField(default=0)
    leave_balance = models.PositiveIntegerField(default=0)

    performance_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboard"

    def __str__(self):
        return self.welcome_title