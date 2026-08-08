from django.urls import path

from . import views


app_name = "teamchat"


urlpatterns = [

    # ======================================================
    # CHAT
    # ======================================================

    path(
        "",
        views.teamchat_view,
        name="chat",
    ),

    # ======================================================
    # MEET
    # ======================================================

    path(
        "meet/",
        views.meet_view,
        name="meet",
    ),

    # ======================================================
    # CALENDAR
    # ======================================================

    path(
        "calendar/",
        views.calendar_view,
        name="calendar",
    ),

    path(
        "calendar/create/",
        views.create_meeting_view,
        name="create_meeting",
    ),

    # ======================================================
    # MESSAGES
    # ======================================================

    path(
        "messages/",
        views.chat_messages_view,
        name="messages",
    ),

    path(
        "send/",
        views.send_message_view,
        name="send_message",
    ),

    path(
        "delete-message/<int:message_id>/",
        views.delete_message_view,
        name="delete_message",
    ),

    # ======================================================
    # GROUPS
    # ======================================================

    path(
        "groups/",
        views.list_groups_view,
        name="groups",
    ),

    path(
        "groups/create/",
        views.create_group_view,
        name="create_group",
    ),

    path(
        "groups/add-members/",
        views.add_group_members_view,
        name="add_members",
    ),

    path(
        "groups/delete/",
        views.delete_group_view,
        name="delete_group",
    ),

    # ======================================================
    # RECORDINGS
    # ======================================================

    path(
        "recordings/upload/",
        views.upload_recording_view,
        name="upload_recording",
    ),

    path(
        "recordings/",
        views.list_recordings_view,
        name="recordings",
    ),

    # ======================================================
    # CALL
    # ======================================================

    path(
        "call/start/",
        views.start_call_notification,
        name="start_call_notification",
    ),

    # ======================================================
    # MEETING ROOM
    # ======================================================

    path(
        "meeting/<str:meeting_id>/",
        views.teamchat_meeting,
        name="teamchat_meeting",
    ),
]