from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        
        ('completed', 'Completed'),
    )

    project_name = models.CharField(max_length=200)

    description = models.TextField(
        blank=True,
        null=True
    )

    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
    )

    role = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    progress = models.IntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )


    


    def __str__(self):
        return self.project_name