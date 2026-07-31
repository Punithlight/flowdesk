from django.contrib import admin
from .models import ChatMessage, Group, GroupMember


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
