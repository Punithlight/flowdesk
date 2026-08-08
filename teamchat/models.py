
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

import secrets
import uuid


User = settings.AUTH_USER_MODEL


# ============================================================
# GROUP
# ============================================================

class Group(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True
    )

    created_by = models.ForeignKey(
        User,
        related_name="created_groups",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# ============================================================
# GROUP MEMBER
# ============================================================

class GroupMember(models.Model):

    group = models.ForeignKey(
        Group,
        related_name="members",
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        related_name="group_memberships",
        on_delete=models.CASCADE
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("group", "user")

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"


# ============================================================
# CHAT MESSAGE
# ============================================================

class ChatMessage(models.Model):

    sender = models.ForeignKey(
        User,
        related_name="sent_messages",
        on_delete=models.CASCADE
    )

    recipient = models.ForeignKey(
        User,
        related_name="received_messages",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    group = models.ForeignKey(
        Group,
        related_name="messages",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    content = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    edited = models.BooleanField(
        default=False
    )

    deleted = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["created_at", "id"]

    def clean(self):

        if not self.recipient and not self.group:
            raise ValidationError(
                "Message must have recipient or group."
            )

        if self.recipient and self.group:
            raise ValidationError(
                "Cannot send to recipient and group together."
            )

    def __str__(self):

        if self.group:
            target = self.group.name
        else:
            target = self.recipient.username

        return f"{self.sender.username} -> {target}"


# ============================================================
# ATTACHMENT
# ============================================================

class Attachment(models.Model):

    message = models.ForeignKey(
        ChatMessage,
        related_name="attachments",
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="chat_attachments/"
    )

    filename = models.CharField(
        max_length=255,
        blank=True
    )

    file_type = models.CharField(
        max_length=100,
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.filename and self.file:
            self.filename = self.file.name.split("/")[-1]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.filename or f"Attachment {self.id}"


# ============================================================
# READ RECEIPT
# ============================================================

class ReadReceipt(models.Model):

    message = models.ForeignKey(
        ChatMessage,
        related_name="read_receipts",
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        related_name="read_messages",
        on_delete=models.CASCADE
    )

    read_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("message", "user")

    def __str__(self):
        return f"{self.user.username} read {self.message.id}"


# ============================================================
# RECORDING
# ============================================================

class Recording(models.Model):
    """
    A saved recording of a call/meeting.
    """

    room_name = models.CharField(
        max_length=150
    )

    group = models.ForeignKey(
        Group,
        related_name="recordings",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    recipient = models.ForeignKey(
        User,
        related_name="recordings_with_me",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    started_by = models.ForeignKey(
        User,
        related_name="recordings_started",
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="call_recordings/%Y/%m/%d/"
    )

    duration_seconds = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Recording {self.id} by {self.started_by.username}"


# ============================================================
# MEETING ID GENERATOR
# ============================================================

def generate_meeting_id():

    while True:

        meeting_id = (
            "FD-"
            + secrets.token_hex(3).upper()
        )

        if not Meeting.objects.filter(
            meeting_id=meeting_id
        ).exists():

            return meeting_id


# ============================================================
# MEETING
# ============================================================

class Meeting(models.Model):

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    venue = models.CharField(
        max_length=255
    )

    # --------------------------------------------------------
    # Meeting date
    # --------------------------------------------------------
    # A default is required because existing Meeting records
    # already exist in the database.
    # --------------------------------------------------------

    date = models.DateField(
        default=timezone.localdate
    )

    # --------------------------------------------------------
    # Meeting time
    # --------------------------------------------------------

    start_time = models.TimeField()

    end_time = models.TimeField()

    # --------------------------------------------------------
    # Created information
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_meetings"
    )

    # --------------------------------------------------------
    # Group
    # --------------------------------------------------------

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meetings"
    )

    # --------------------------------------------------------
    # FlowDesk Meeting ID
    # --------------------------------------------------------

    meeting_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    def save(self, *args, **kwargs):

        if not self.meeting_id:

            self.meeting_id = (
                "FD-"
                + uuid.uuid4().hex[:6].upper()
            )

        super().save(*args, **kwargs)

    # --------------------------------------------------------
    # String representation
    # --------------------------------------------------------

    def __str__(self):
        return self.title

