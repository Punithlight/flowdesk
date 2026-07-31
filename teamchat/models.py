from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

User = settings.AUTH_USER_MODEL


class Group(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_by = models.ForeignKey(User, related_name="created_groups", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    group = models.ForeignKey(Group, related_name="members", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="group_memberships", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ("group", "user")

    def __str__(self):
        return f"{self.user} @ {self.group.name}"


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, related_name="messages", on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ("created_at", "id")

    def clean(self):
        # enforce that message has exactly one target: recipient xor group
        if not (self.recipient or self.group):
            raise ValidationError("Message must have a recipient or a group.")
        if self.recipient and self.group:
            raise ValidationError("Message cannot have both recipient and group.")

    def __str__(self):
        target = self.recipient.username if self.recipient else (self.group.name if self.group else "unspecified")
        return f"{self.sender.username} -> {target}: {self.content[:40]}"


class Attachment(models.Model):
    message = models.ForeignKey(ChatMessage, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="chat_attachments/%Y/%m/%d")
    filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename or self.file.name


class ReadReceipt(models.Model):
    message = models.ForeignKey(ChatMessage, related_name="read_receipts", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="read_receipts", on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")

    def __str__(self):
        return f"{self.user} read {self.message.id} at {self.read_at}"
