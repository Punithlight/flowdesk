import json
import uuid
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from employees.models import Employee

from .models import (
    ChatMessage,
    Group,
    GroupMember,
    Recording,
    Attachment,
    Meeting,
)

User = get_user_model()


# ==========================================================
# CHAT HOME
# ==========================================================

@login_required(login_url="login")
def teamchat_view(request):

    employees = (
        Employee.objects
        .select_related("user")
        .exclude(user=request.user)
        .order_by(
            "user__first_name",
            "user__username"
        )
    )

    groups = (
        Group.objects
        .prefetch_related("members__user")
        .all()
        .order_by("name")
    )

    return render(
        request,
        "teamchat/chat.html",
        {
            "employees": employees,
            "groups": groups,
        }
    )


# ==========================================================
# MEETING CHAT
# ==========================================================

@login_required(login_url="login")
def teamchat_meeting(request, meeting_id):

    meeting = get_object_or_404(
        Meeting,
        meeting_id=meeting_id
    )

    employees = (
        Employee.objects
        .select_related("user")
        .exclude(user=request.user)
        .order_by(
            "user__first_name",
            "user__username"
        )
    )

    groups = (
        Group.objects
        .prefetch_related("members__user")
        .all()
        .order_by("name")
    )

    # ------------------------------------------------------
    # Because Meeting.group is NOT a ForeignKey,
    # group contains the group ID.
    # ------------------------------------------------------

    meeting_group_id = meeting.group

    meeting_group = None

    if meeting_group_id:

        meeting_group = (
            Group.objects
            .filter(id=meeting_group_id)
            .first()
        )

    return render(
        request,
        "teamchat/chat.html",
        {
            "employees": employees,
            "groups": groups,
            "meeting": meeting,

            "meeting_group_id": meeting_group_id,

            "meeting_group": meeting_group,
        }
    )


# ==========================================================
# MEET PAGE
# ==========================================================

@login_required(login_url="login")
def meet_view(request):

    # ======================================================
    # GROUPS AVAILABLE TO CURRENT USER
    # ======================================================

    groups = (
        Group.objects
        .filter(
            members__user=request.user
        )
        .prefetch_related("members__user")
        .distinct()
        .order_by("name")
    )

    # ------------------------------------------------------
    # Create dictionary:
    #
    # {
    #     group_id: group_object
    # }
    #
    # Since Meeting.group is not a ForeignKey,
    # we cannot use meeting.group.name.
    # ------------------------------------------------------

    group_map = {
        group.id: group
        for group in groups
    }

    # ======================================================
    # MEETINGS CREATED BY CURRENT USER
    # ======================================================

    meetings = (
        Meeting.objects
        .filter(
            created_by=request.user
        )
        .select_related(
            "created_by"
        )
        .order_by(
            "-created_at"
        )
    )

    # ======================================================
    # UPCOMING MEETINGS
    #
    # IMPORTANT:
    #
    # start_time is a TIME field.
    # Therefore this is WRONG:
    #
    # start_time__gte=timezone.now()
    #
    # because timezone.now() is DATETIME.
    #
    # ======================================================

    today = timezone.localdate()
    current_time = timezone.localtime().time()

    upcoming_meetings = (
        meetings
        .filter(
            Q(date__gt=today)
            |
            Q(
                date=today,
                start_time__gte=current_time
            )
        )
        .order_by(
            "date",
            "start_time"
        )[:10]
    )

    # ======================================================
    # RECENT MEETINGS
    # ======================================================

    recent_meetings = (
        meetings
        .order_by(
            "-created_at"
        )[:10]
    )

    # ======================================================
    # ADD GROUP OBJECT TO EACH MEETING
    # ======================================================

    for meeting in recent_meetings:

        meeting.display_group = group_map.get(
            meeting.group
        )

    for meeting in upcoming_meetings:

        meeting.display_group = group_map.get(
            meeting.group
        )

    # ======================================================
    # OTHER USERS
    # ======================================================

    users = (
        User.objects
        .exclude(
            id=request.user.id
        )
        .order_by(
            "first_name",
            "username"
        )
    )

    # ======================================================
    # RENDER
    # ======================================================

    return render(
        request,
        "teamchat/meet.html",
        {
            "groups": groups,

            "meetings": meetings,

            "upcoming_meetings":
                upcoming_meetings,

            "recent_meetings":
                recent_meetings,

            "users": users,
        }
    )


# ==========================================================
# SEND MESSAGE
# ==========================================================

@login_required(login_url="login")
@require_http_methods(["POST"])
def send_message_view(request):

    if request.content_type.startswith("multipart"):

        recipient_id = request.POST.get(
            "recipient_id"
        )

        content = request.POST.get(
            "content",
            ""
        ).strip()

    else:

        try:

            body = json.loads(
                request.body
            )

        except Exception:

            return JsonResponse(
                {
                    "error":
                        "Invalid JSON"
                },
                status=400
            )

        recipient_id = body.get(
            "recipient_id"
        )

        content = body.get(
            "content",
            ""
        ).strip()

    if not recipient_id:

        return JsonResponse(
            {
                "error":
                    "Recipient required"
            },
            status=400
        )

    files = request.FILES.getlist(
        "attachments"
    )

    if not content and not files:

        return JsonResponse(
            {
                "error":
                    "Message cannot be empty"
            },
            status=400
        )

    # ======================================================
    # GROUP MESSAGE
    # ======================================================

    if str(recipient_id).startswith("group:"):

        group = get_object_or_404(
            Group,
            id=recipient_id.split(":")[1]
        )

        message = ChatMessage.objects.create(
            sender=request.user,
            group=group,
            content=content
        )

    # ======================================================
    # PRIVATE MESSAGE
    # ======================================================

    else:

        recipient = get_object_or_404(
            User,
            id=recipient_id
        )

        message = ChatMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )

    # ======================================================
    # ATTACHMENTS
    # ======================================================

    for file in files:

        Attachment.objects.create(
            message=message,
            file=file,
            filename=file.name,
            file_type=file.content_type
        )

    return JsonResponse(
        {
            "success": True,
            "id": message.id,
            "sender": message.sender.id,
            "content": message.content,
        }
    )


# ==========================================================
# DELETE MESSAGE
# ==========================================================

@login_required(login_url="login")
@require_http_methods(["POST", "DELETE"])
def delete_message_view(
    request,
    message_id
):

    message = get_object_or_404(
        ChatMessage,
        id=message_id,
        sender=request.user
    )

    message.delete()

    return JsonResponse(
        {
            "success": True,
            "status": "deleted"
        }
    )


# ==========================================================
# LOAD CHAT MESSAGES
# ==========================================================

@login_required(login_url="login")
def chat_messages_view(request):

    recipient_id = request.GET.get(
        "recipient_id"
    )

    if not recipient_id:

        return JsonResponse(
            {
                "messages": []
            }
        )

    # ======================================================
    # GROUP CHAT
    # ======================================================

    if str(recipient_id).startswith("group:"):

        group = get_object_or_404(
            Group,
            id=recipient_id.split(":")[1]
        )

        messages_qs = (
            ChatMessage.objects
            .filter(group=group)
            .select_related("sender")
            .prefetch_related("attachments")
            .order_by("created_at")
        )

    # ======================================================
    # PRIVATE CHAT
    # ======================================================

    else:

        recipient = get_object_or_404(
            User,
            id=recipient_id
        )

        messages_qs = (
            ChatMessage.objects
            .filter(
                Q(
                    sender=request.user,
                    recipient=recipient
                )
                |
                Q(
                    sender=recipient,
                    recipient=request.user
                )
            )
            .select_related(
                "sender",
                "recipient"
            )
            .prefetch_related(
                "attachments"
            )
            .order_by("created_at")
        )

    data = []

    for msg in messages_qs:

        data.append(
            {
                "id": msg.id,

                "content":
                    msg.content,

                "sender":
                    msg.sender.id,

                "sender_id":
                    msg.sender.id,

                "sender_name":
                    (
                        msg.sender.get_full_name()
                        or msg.sender.username
                    ),

                "recipient":
                    (
                        msg.recipient.id
                        if msg.recipient
                        else None
                    ),

                "attachments": [

                    {
                        "url": att.file.url,
                        "filename": att.filename,
                        "file_type": att.file_type
                    }

                    for att
                    in msg.attachments.all()

                ],

                "created_at":
                    timezone.localtime(
                        msg.created_at
                    ).strftime(
                        "%I:%M %p"
                    ),
            }
        )

    return JsonResponse(
        {
            "messages": data
        }
    )


# ==========================================================
# LIST GROUPS
# ==========================================================

@login_required(login_url="login")
def list_groups_view(request):

    groups = (
        Group.objects
        .prefetch_related(
            "members__user"
        )
        .all()
    )

    result = []

    for group in groups:

        members = []

        for member in group.members.all():

            members.append(
                {
                    "id":
                        member.user.id,

                    "name":
                        (
                            member.user.get_full_name()
                            or member.user.username
                        ),

                    "email":
                        member.user.email,
                }
            )

        result.append(
            {
                "id":
                    group.id,

                "name":
                    group.name,

                "members":
                    members,
            }
        )

    return JsonResponse(
        {
            "groups":
                result
        }
    )


# ==========================================================
# CREATE GROUP
# ==========================================================

@login_required(login_url="login")
@require_http_methods(["POST"])
def create_group_view(request):

    try:

        body = json.loads(
            request.body
        )

    except Exception:

        return JsonResponse(
            {
                "error":
                    "Invalid JSON"
            },
            status=400
        )

    name = body.get(
        "name",
        ""
    ).strip()

    if not name:

        return JsonResponse(
            {
                "error":
                    "Group name required"
            },
            status=400
        )

    group = Group.objects.create(
        name=name,
        created_by=request.user
    )

    GroupMember.objects.create(
        group=group,
        user=request.user
    )

    return JsonResponse(
        {
            "success": True,
            "id": group.id,
            "name": group.name,
        }
    )


# ==========================================================
# ADD MEMBERS
# ==========================================================

@login_required(login_url="login")
@require_http_methods(["POST"])
def add_group_members_view(request):

    try:

        body = json.loads(
            request.body
        )

    except Exception:

        return JsonResponse(
            {
                "error":
                    "Invalid JSON"
            },
            status=400
        )

    group = get_object_or_404(
        Group,
        id=body.get("group_id")
    )

    added = 0

    for uid in body.get(
        "member_ids",
        []
    ):

        user = (
            User.objects
            .filter(id=uid)
            .first()
        )

        if user:

            _, created = (
                GroupMember.objects
                .get_or_create(
                    group=group,
                    user=user
                )
            )

            if created:
                added += 1

    return JsonResponse(
        {
            "success": True,
            "added": added
        }
    )


# ==========================================================
# DELETE GROUP
# ==========================================================

@login_required(login_url="login")
@require_http_methods(["POST"])
def delete_group_view(request):

    try:

        body = json.loads(
            request.body
        )

    except Exception:

        return JsonResponse(
            {
                "error":
                    "Invalid JSON"
            },
            status=400
        )

    group = get_object_or_404(
        Group,
        id=body.get("group_id")
    )

    group.delete()

    return JsonResponse(
        {
            "success": True
        }
    )


# ==========================================================
# UPLOAD CALL RECORDING
# ==========================================================

@login_required(login_url="login")
@require_http_methods(["POST"])
def upload_recording_view(request):

    recipient_id = request.POST.get(
        "recipient_id",
        ""
    )

    room_name = request.POST.get(
        "room_name",
        ""
    )

    duration_raw = request.POST.get(
        "duration",
        0
    )

    upload = request.FILES.get(
        "file"
    )

    if not upload:

        return JsonResponse(
            {
                "error":
                    "No recording file received"
            },
            status=400
        )

    try:

        duration = int(
            float(duration_raw)
        )

    except (
        TypeError,
        ValueError
    ):

        duration = 0

    recording = Recording(
        room_name=room_name,
        started_by=request.user,
        duration_seconds=duration,
    )

    group = None
    recipient = None

    if str(recipient_id).startswith(
        "group:"
    ):

        group = (
            Group.objects
            .filter(
                id=recipient_id.split(":")[1]
            )
            .first()
        )

        recording.group = group

    elif recipient_id:

        recipient = (
            User.objects
            .filter(
                id=recipient_id
            )
            .first()
        )

        recording.recipient = recipient

    recording.file.save(
        upload.name,
        upload,
        save=False
    )

    recording.save()

    minutes, seconds = divmod(
        duration,
        60
    )

    length_label = (
        f"{minutes}:{seconds:02d}"
    )

    filename = (
        recording.file.name
        .split("/")[-1]
    )

    marker = (
        f"[[recording:"
        f"{recording.file.url}|"
        f"{filename}|"
        f"{length_label}]]"
    )

    message = None

    if group:

        message = ChatMessage.objects.create(
            sender=request.user,
            group=group,
            content=marker
        )

    elif recipient:

        message = ChatMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            content=marker
        )

    return JsonResponse(
        {
            "success": True,

            "id":
                recording.id,

            "url":
                recording.file.url,

            "duration":
                length_label,

            "message_id":
                (
                    message.id
                    if message
                    else None
                ),
        }
    )


# ==========================================================
# LIST CALL RECORDINGS
# ==========================================================

@login_required(login_url="login")
def list_recordings_view(request):

    recordings = (
        Recording.objects
        .filter(
            Q(
                started_by=request.user
            )
            |
            Q(
                recipient=request.user
            )
            |
            Q(
                group__members__user=request.user
            )
        )
        .distinct()
        .select_related(
            "started_by",
            "recipient",
            "group"
        )
    )

    data = []

    for rec in recordings:

        if rec.group:

            target = rec.group.name

        elif rec.recipient:

            target = (
                rec.recipient.get_full_name()
                or rec.recipient.username
            )

        else:

            target = "Call"

        minutes, seconds = divmod(
            rec.duration_seconds,
            60
        )

        data.append(
            {
                "id":
                    rec.id,

                "url":
                    rec.file.url,

                "filename":
                    rec.file.name.split("/")[-1],

                "target":
                    target,

                "started_by":
                    (
                        rec.started_by.get_full_name()
                        or rec.started_by.username
                    ),

                "duration":
                    f"{minutes}:{seconds:02d}",

                "created_at":
                    timezone.localtime(
                        rec.created_at
                    ).strftime(
                        "%d-%m-%Y %I:%M %p"
                    ),
            }
        )

    return JsonResponse(
        {
            "recordings": data
        }
    )


# ==========================================================
# CALL NOTIFICATION
# ==========================================================

@login_required
@require_http_methods(["POST"])
def start_call_notification(request):

    try:

        body = json.loads(
            request.body
        )

    except Exception:

        return JsonResponse(
            {
                "error":
                    "Invalid JSON"
            },
            status=400
        )

    recipient_id = body.get(
        "recipient_id"
    )

    room_name = body.get(
        "room_name"
    )

    call_type = body.get(
        "call_type",
        "video"
    )

    channel_layer = get_channel_layer()

    async_to_sync(
        channel_layer.group_send
    )(
        f"user_{recipient_id}",
        {
            "type":
                "notify_call",

            "caller_id":
                request.user.id,

            "caller_name":
                (
                    request.user.get_full_name()
                    or request.user.username
                ),

            "room_name":
                room_name,

            "call_type":
                call_type,
        },
    )

    return JsonResponse(
        {
            "success": True
        }
    )


# ==========================================================
# CALENDAR
# ==========================================================

@login_required(login_url="login")
def calendar_view(request):

    today = timezone.localdate()

    # ======================================================
    # WEEK OFFSET
    # ======================================================

    try:

        week_offset = int(
            request.GET.get(
                "week",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        week_offset = 0

    # ======================================================
    # MONDAY
    # ======================================================

    monday = (
        today
        - timedelta(
            days=today.weekday()
        )
        + timedelta(
            weeks=week_offset
        )
    )

    # Monday -> Friday

    week_days = [
        monday + timedelta(days=i)
        for i in range(5)
    ]

    month_title = monday.strftime(
        "%B %Y"
    )

    # ======================================================
    # USER GROUPS
    # ======================================================

    user_groups = (
        Group.objects
        .filter(
            members__user=request.user
        )
        .prefetch_related(
            "members__user"
        )
        .distinct()
        .order_by("name")
    )

    # ======================================================
    # GROUP IDS
    #
    # Meeting.group is NOT a ForeignKey.
    # ======================================================

    group_ids = user_groups.values_list(
        "id",
        flat=True
    )

    # ======================================================
    # MEETINGS
    # ======================================================

    meetings = (
        Meeting.objects
        .filter(
            group__in=group_ids,
            date__range=(
                week_days[0],
                week_days[-1]
            )
        )
        .select_related(
            "created_by"
        )
        .order_by(
            "date",
            "start_time"
        )
    )

    # ======================================================
    # CALENDAR SETTINGS
    # ======================================================

    calendar_start_hour = 9

    pixels_per_minute = 1.55

    calendar_events = []

    # ======================================================
    # BUILD EVENTS
    # ======================================================

    for meeting in meetings:

        meeting_date = meeting.date

        start_time = meeting.start_time

        end_time = meeting.end_time

        start_minutes = (
            start_time.hour * 60
            + start_time.minute
        )

        end_minutes = (
            end_time.hour * 60
            + end_time.minute
        )

        top = (
            start_minutes
            - calendar_start_hour * 60
        ) * pixels_per_minute

        height = (
            end_minutes
            - start_minutes
        ) * pixels_per_minute

        day_index = (
            meeting_date - monday
        ).days

        if day_index < 0 or day_index > 4:
            continue

        left = day_index * 20

        calendar_events.append(
            {
                "meeting":
                    meeting,

                "date":
                    meeting_date,

                "start":
                    start_time,

                "end":
                    end_time,

                "day_index":
                    day_index,

                "left":
                    left,

                "top":
                    top,

                "height":
                    max(
                        height,
                        45
                    ),
            }
        )

    # ======================================================
    # HOURS
    # ======================================================

    hours = range(
        9,
        19
    )

    # ======================================================
    # RENDER
    # ======================================================

    return render(
        request,
        "teamchat/calendar.html",
        {
            "calendar_events":
                calendar_events,

            "groups":
                user_groups,

            "month_title":
                month_title,

            "today":
                today,

            "week_days":
                week_days,

            "week_offset":
                week_offset,

            "hours":
                hours,
        }
    )


# ==========================================================
# CREATE MEETING
# ==========================================================

@login_required(login_url="login")
@require_http_methods(["POST"])
def create_meeting_view(request):

    title = request.POST.get(
        "title",
        ""
    ).strip()

    group_id = request.POST.get(
        "group_id"
    )

    description = request.POST.get(
        "description",
        ""
    ).strip()

    date_value = request.POST.get(
        "date"
    )

    start_value = request.POST.get(
        "start_time"
    )

    end_value = request.POST.get(
        "end_time"
    )

    venue = request.POST.get(
        "venue",
        "Virtual Meeting"
    ).strip()

    # ======================================================
    # TITLE
    # ======================================================

    if not title:

        messages.error(
            request,
            "Meeting title is required."
        )

        return redirect(
            "teamchat:meet"
        )

    # ======================================================
    # GROUP
    # ======================================================

    if not group_id:

        messages.error(
            request,
            "Please select a group."
        )

        return redirect(
            "teamchat:meet"
        )

    # ======================================================
    # GET GROUP
    # ======================================================

    group = get_object_or_404(
        Group,
        id=group_id
    )

    # ======================================================
    # CHECK MEMBERSHIP
    # ======================================================

    is_member = (
        GroupMember.objects
        .filter(
            group=group,
            user=request.user
        )
        .exists()
    )

    if not is_member:

        messages.error(
            request,
            "You are not a member of the selected group."
        )

        return redirect(
            "teamchat:meet"
        )

    # ======================================================
    # VALIDATE DATE/TIME
    # ======================================================

    if (
        not date_value
        or not start_value
        or not end_value
    ):

        messages.error(
            request,
            "Date, start time and end time are required."
        )

        return redirect(
            "teamchat:meet"
        )

    # ======================================================
    # CONVERT VALUES
    # ======================================================

    try:

        meeting_date = datetime.strptime(
            date_value,
            "%Y-%m-%d"
        ).date()

        start_time = datetime.strptime(
            start_value,
            "%H:%M"
        ).time()

        end_time = datetime.strptime(
            end_value,
            "%H:%M"
        ).time()

    except ValueError:

        messages.error(
            request,
            "Invalid date or time."
        )

        return redirect(
            "teamchat:meet"
        )

    # ======================================================
    # CHECK TIME
    # ======================================================

    if end_time <= start_time:

        messages.error(
            request,
            "End time must be after start time."
        )

        return redirect(
            "teamchat:meet"
        )

    # ======================================================
    # CHECK PAST DATE/TIME
    # ======================================================

    start_datetime = datetime.combine(
        meeting_date,
        start_time
    )

    start_datetime = timezone.make_aware(
        start_datetime
    )

    if start_datetime < timezone.now():

        messages.error(
            request,
            "Meeting date and start time cannot be in the past."
        )

        return redirect(
            "teamchat:meet"
        )

    # ======================================================
    # CREATE MEETING
    #
    # IMPORTANT:
    #
    # Meeting.group is NOT a ForeignKey.
    #
    # Therefore save the group ID:
    #
    # group=group.id
    #
    # NOT:
    #
    # group=group
    #
    # ======================================================

    meeting = Meeting.objects.create(

        title=title,

        description=description,

        group=group.id,

        date=meeting_date,

        start_time=start_time,

        end_time=end_time,

        venue=venue or "Virtual Meeting",

        created_by=request.user,
    )

    # ======================================================
    # SUCCESS
    # ======================================================

    messages.success(
        request,
        (
            "Meeting created successfully! "
            f"Meeting ID: {meeting.meeting_id}"
        )
    )

    return redirect(
        "teamchat:meet"
    )