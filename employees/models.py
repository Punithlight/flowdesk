from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):

    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("Manager", "Manager"),
        ("HR", "HR"),
        ("Team Lead", "Team Lead"),
        ("Employee", "Employee"),
    ]

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
        ("Prefer not to say", "Prefer not to say"),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ("Full-Time", "Full-Time"),
        ("Part-Time", "Part-Time"),
        ("Contract", "Contract"),
        ("Intern", "Intern"),
    ]

    # ===========================
    # Basic Information
    # ===========================

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True
    )

    department = models.CharField(
        max_length=100
    )

    designation = models.CharField(
        max_length=100
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="Employee"
    )

    phone = models.CharField(
        max_length=15
    )

    joining_date = models.DateField()

    profile_image = models.ImageField(
        upload_to="employees/",
        blank=True,
        null=True
    )

    # ===========================
    # Personal Information
    # ===========================

    dob = models.DateField(
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=30,
        choices=GENDER_CHOICES,
        blank=True
    )

    blood_group = models.CharField(
        max_length=5,
        blank=True
    )

    present_address = models.TextField(
        blank=True
    )

    permanent_address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True
    )

    emergency_contact = models.CharField(
        max_length=15,
        blank=True
    )

    # ===========================
    # Professional Details
    # ===========================

    reporting_manager = models.CharField(
        max_length=100,
        blank=True
    )

    team_name = models.CharField(
        max_length=100,
        blank=True
    )

    work_location = models.CharField(
        max_length=100,
        blank=True
    )

    employment_type = models.CharField(
        max_length=30,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default="Full-Time"
    )

    # ===========================
    # Record Information
    # ===========================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"