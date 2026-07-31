from django.urls import path
from . import views

urlpatterns = [
    path("", views.teamchat_view, name="teamchat"),
    path("messages/", views.chat_messages_view, name="teamchat_messages"),
    path("send/", views.send_message_view, name="teamchat_send"),
    path("groups/", views.list_groups_view, name="teamchat_groups"),
    path("groups/create/", views.create_group_view, name="teamchat_groups_create"),
    path("groups/add-members/", views.add_group_members_view, name="teamchat_groups_add_members"),
    path("groups/delete/", views.delete_group_view, name="teamchat_groups_delete"),
]
