from django.db import models
from employees.models import Employee


class Report(models.Model):

    # ==========================================================
    # REPORT TYPES
    # ==========================================================

    REPORT_TYPE_CHOICES = [
        ("employee", "Employee Report"),
        ("manager", "Manager / Team Lead Report"),
    ]

    # ==========================================================
    # REPORT STATUS
    # ==========================================================

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("sent", "Sent"),
    ]

    # ==========================================================
    # EMPLOYEE / TEAM LEAD
    # ==========================================================

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="reports"
    )

    # ==========================================================
    # REPORT TYPE
    # ==========================================================

    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        default="employee"
    )

    # ==========================================================
    # DEPARTMENT
    # ==========================================================

    department = models.CharField(
        max_length=100,
        blank=True
    )

    # ==========================================================
    # REPORT TITLE
    # ==========================================================

    title = models.CharField(
        max_length=200
    )

    # ==========================================================
    # REPORT CONTENT
    # ==========================================================

    report_text = models.TextField()

    # ==========================================================
    # ATTACHMENT
    # ==========================================================

    attachment = models.FileField(
        upload_to="reports/",
        blank=True,
        null=True
    )

    # ==========================================================
    # REPORT STATUS
    # ==========================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    # ==========================================================
    # SUBMITTED / SENT DATE
    # ==========================================================

    submitted_at = models.DateTimeField(
        blank=True,
        null=True
    )

    # ==========================================================
    # CREATED DATE
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # ==========================================================
    # UPDATED DATE
    # ==========================================================

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(self):
        employee_name = self.employee.user.get_full_name()

        if not employee_name:
            employee_name = self.employee.user.username

        return f"{self.title} - {employee_name}"

    # ==========================================================
    # EMPLOYEE NAME
    # ==========================================================

    @property
    def employee_name(self):
        name = self.employee.user.get_full_name()

        if name:
            return name

        return self.employee.user.username

    # ==========================================================
    # EMPLOYEE ROLE
    # ==========================================================

    @property
    def employee_role(self):
        return self.employee.role

    # ==========================================================
    # REPORT TYPE DISPLAY
    # ==========================================================

    @property
    def report_type_display(self):
        return self.get_report_type_display()

    # ==========================================================
    # STATUS DISPLAY
    # ==========================================================

    @property
    def status_display(self):
        return self.get_status_display()

    # ==========================================================
    # CHECK TEAM LEAD / MANAGER REPORT
    # ==========================================================

    @property
    def is_team_lead_report(self):
        return self.report_type == "manager"

    # ==========================================================
    # CHECK EMPLOYEE REPORT
    # ==========================================================

    @property
    def is_employee_report(self):
        return self.report_type == "employee"

    # ==========================================================
    # CHECK SENT
    # ==========================================================

    @property
    def is_sent(self):
        return self.status == "sent"

    # ==========================================================
    # CHECK DRAFT
    # ==========================================================

    @property
    def is_draft(self):
        return self.status == "draft"

    # ==========================================================
    # CHECK SUBMITTED
    # ==========================================================

    @property
    def is_submitted(self):
        return self.status == "submitted"