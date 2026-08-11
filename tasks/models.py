from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User

from employees.models import Employee
from projects.models import Project


class Task(models.Model):

    # ==========================================================
    # CHOICES
    # ==========================================================

    PRIORITY = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    STATUS = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Review", "Review"),
        ("Completed", "Completed"),
    ]

    APPROVAL_STATUS = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    # ==========================================================
    # PROJECT
    # ==========================================================

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_tasks",
        null=True,
        blank=True
    )

    # ==========================================================
    # EMPLOYEE WHO RECEIVES THE TASK
    # ==========================================================

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employee_tasks"
    )

    # ==========================================================
    # USER WHO ASSIGNED THE TASK
    # ==========================================================

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks"
    )

    # ==========================================================
    # TASK INFORMATION
    # ==========================================================

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True,
        null=True
    )

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

    # ==========================================================
    # DATES
    # ==========================================================

    start_date = models.DateField(
        null=True,
        blank=True
    )

    due_date = models.DateField()

    # ==========================================================
    # TIME
    # ==========================================================

    start_time = models.TimeField(
        blank=True,
        null=True
    )

    end_time = models.TimeField(
        blank=True,
        null=True
    )

    # ==========================================================
    # EMPLOYEE UPDATE
    # ==========================================================

    progress = models.PositiveIntegerField(
        default=0,
        validators=[
            MaxValueValidator(100)
        ]
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

    # ==========================================================
    # MANAGER APPROVAL
    # ==========================================================

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default="Pending"
    )

    manager_comment = models.TextField(
        blank=True,
        null=True
    )

    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ==========================================================
    # META
    # ==========================================================

    class Meta:
        ordering = [
            "due_date"
        ]

        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    # ==========================================================
    # STRING
    # ==========================================================

    def __str__(self):
        return f"{self.title} - {self.employee}"