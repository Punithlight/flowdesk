from django.db import models
from django.conf import settings


class UserSettings(models.Model):

    THEME_CHOICES = [
        ("light", "Light"),
        ("dark", "Dark"),
        ("system", "System"),
    ]

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("en-us", "English (US)"),
        ("en-gb", "English (UK)"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("de", "German"),
        ("hi", "Hindi"),
        ("kn", "Kannada"),
    ]

    LAYOUT_CHOICES = [
        ("compact", "Compact"),
        ("comfortable", "Comfortable"),
        ("detailed", "Detailed"),
    ]

    TWO_FACTOR_CHOICES = [
        ("auth-app", "Authenticator App"),
        ("sms", "SMS"),
        ("email", "Email"),
        ("whatsapp", "WhatsApp"),
    ]

    BIOMETRIC_CHOICES = [
        ("fingerprint", "Fingerprint"),
        ("faceid", "Face ID"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_settings"
    )

    # ---------------- Security ----------------

    two_fa_enabled = models.BooleanField(default=False)

    two_fa_method = models.CharField(
        max_length=30,
        choices=TWO_FACTOR_CHOICES,
        default="auth-app"
    )

    biometric_enabled = models.BooleanField(default=False)

    biometric_type = models.CharField(
        max_length=20,
        choices=BIOMETRIC_CHOICES,
        default="fingerprint"
    )

    recovery_email = models.EmailField(blank=True)

    recovery_phone = models.CharField(
        max_length=20,
        blank=True
    )

    security_question = models.TextField(blank=True)

    # ---------------- Appearance ----------------

    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default="light"
    )

    font_size = models.IntegerField(default=16)

    high_contrast = models.BooleanField(default=False)

    # ---------------- Notifications ----------------

    notify_email = models.BooleanField(default=True)

    notify_push = models.BooleanField(default=True)

    notify_attendance = models.BooleanField(default=True)

    notify_announcements = models.BooleanField(default=True)

    # ---------------- Language ----------------

    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default="en"
    )

    date_format = models.CharField(
        max_length=30,
        default="dd-mm-yyyy"
    )

    time_format = models.CharField(
        max_length=10,
        default="12"
    )

    timezone = models.CharField(
        max_length=100,
        default="Asia/Kolkata"
    )

    # ---------------- Dashboard ----------------

    dashboard_layout = models.CharField(
        max_length=30,
        choices=LAYOUT_CHOICES,
        default="compact"
    )

    dashboard_widgets = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Settings"


class LoginHistory(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="login_history"
    )

    login_time = models.DateTimeField(auto_now_add=True)

    device = models.CharField(max_length=150)

    location = models.CharField(
        max_length=150,
        default="Unknown"
    )

    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class ActiveSession(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="active_sessions"
    )

    session_key = models.CharField(max_length=100)

    device = models.CharField(max_length=150)

    location = models.CharField(
        max_length=150,
        default="Unknown"
    )

    ip_address = models.GenericIPAddressField()

    login_time = models.DateTimeField(auto_now_add=True)

    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.device}"


class Support(models.Model):

    title = models.CharField(max_length=100)

    description = models.TextField()

    email = models.EmailField(blank=True)

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title