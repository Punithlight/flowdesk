from django.db import models
from django.core.validators import MaxValueValidator
from employees.models import Employee
from projects.models import Project


class tasks(models.Model):

    PRIORITY = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Review', 'Review'),
        ('Completed', 'Completed'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY,
        default="Medium"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default="Pending"
    )

    due_date = models.DateField()

    start_time = models.TimeField(
        blank=True,
        null=True
    )

    end_time = models.TimeField(
        blank=True,
        null=True
    )

    # Employee Update Fields

    progress = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)]
    )

    employee_comment = models.TextField(
        blank=True,
        null=True
    )

    attachment = models.FileField(
        upload_to="task_files/",
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
        ordering = ["due_date"]

    def __str__(self):
        return self.title