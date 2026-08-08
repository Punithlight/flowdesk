from django.contrib import admin
from .models import ChatMessage, Group, GroupMember, Recording


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "group", "content", "created_at")
    search_fields = ("content", "sender__username", "recipient__username", "group__name")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")
    search_fields = ("name",)


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ("group", "user")
    search_fields = ("user__username",)


@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ("id", "started_by", "group", "recipient", "duration_seconds", "created_at")
    search_fields = ("room_name", "started_by__username")
