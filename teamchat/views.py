import json

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import ChatMessage
from .models import Group, GroupMember


@login_required(login_url="login")
def teamchat_view(request):
    return render(request, "teamchat/chat.html")


@login_required(login_url="login")
def chat_messages_view(request):
    recipient_id = request.GET.get("recipient_id")
    if recipient_id:
        # Group chat id format: group:<id>
        if str(recipient_id).startswith('group:'):
            try:
                gid = int(str(recipient_id).split(':', 1)[1])
                group = Group.objects.filter(id=gid).first()
            except (ValueError, TypeError):
                group = None
            if group:
                messages = ChatMessage.objects.filter(group=group).order_by("created_at", "id")
            else:
                messages = ChatMessage.objects.none()
        else:
            recipient = request.user.__class__.objects.filter(id=recipient_id).first()
            if recipient is None:
                messages = ChatMessage.objects.filter(sender=request.user) | ChatMessage.objects.filter(recipient=request.user)
                messages = messages.order_by("created_at", "id")
            else:
                messages = ChatMessage.objects.filter(
                    (models.Q(sender=request.user, recipient=recipient) | models.Q(sender=recipient, recipient=request.user))
                ).order_by("created_at", "id")
    else:
        messages = ChatMessage.objects.filter(sender=request.user) | ChatMessage.objects.filter(recipient=request.user)
        messages = messages.order_by("created_at", "id")

    data = []
    for message in messages:
        data.append(
            {
                "id": message.id,
                "sender": message.sender.id,
                "sender_username": message.sender.username,
                "recipient": message.recipient.id if message.recipient else None,
                "group_id": message.group.id if message.group else None,
                "group_name": message.group.name if message.group else None,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
        )
    return JsonResponse({"messages": data})


@login_required(login_url="login")
@require_http_methods(["POST"])
def send_message_view(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    recipient_id = payload.get("recipient_id")
    content = (payload.get("content") or "").strip()
    if not content:
        return JsonResponse({"error": "Message content is required"}, status=400)

    recipient = None
    group = None
    if recipient_id:
        if str(recipient_id).startswith('group:'):
            try:
                gid = int(str(recipient_id).split(':', 1)[1])
                group = Group.objects.filter(id=gid).first()
            except (ValueError, TypeError):
                group = None
        else:
            recipient = request.user.__class__.objects.filter(id=recipient_id).first()

    message = ChatMessage.objects.create(sender=request.user, recipient=recipient, group=group, content=content)
    return JsonResponse(
        {
            "id": message.id,
            "sender": message.sender.id,
            "sender_username": message.sender.username,
            "recipient": message.recipient.id if message.recipient else None,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        }
    )



@login_required(login_url="login")
@require_http_methods(["GET"])
def list_groups_view(request):
    groups = Group.objects.all().order_by('name')
    data = []
    for g in groups:
        members = [m.member_identifier for m in g.members.all()]
        data.append({"id": g.id, "name": g.name, "members": members})
    return JsonResponse({"groups": data})


@login_required(login_url="login")
@require_http_methods(["POST"])
def create_group_view(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    name = (payload.get('name') or '').strip()
    if not name:
        return JsonResponse({"error": "Group name required"}, status=400)
    group, created = Group.objects.get_or_create(name=name, defaults={'created_by': request.user})
    return JsonResponse({"id": group.id, "name": group.name, "created": created})


@login_required(login_url="login")
@require_http_methods(["POST"])
def add_group_members_view(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    group_id = payload.get('group_id')
    member_ids = payload.get('member_ids') or []
    if not group_id:
        return JsonResponse({"error": "group_id required"}, status=400)
    group = Group.objects.filter(id=group_id).first()
    if not group:
        return JsonResponse({"error": "group not found"}, status=404)
    created = 0
    for mid in member_ids:
        identifier = str(mid)
        obj, was_created = GroupMember.objects.get_or_create(group=group, member_identifier=identifier)
        if was_created:
            created += 1
    members = [m.member_identifier for m in group.members.all()]
    return JsonResponse({"group_id": group.id, "members": members, "added": created})


@login_required(login_url="login")
@require_http_methods(["POST"])
def delete_group_view(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    group_id = payload.get('group_id')
    if not group_id:
        return JsonResponse({"error": "group_id required"}, status=400)
    group = Group.objects.filter(id=group_id).first()
    if not group:
        return JsonResponse({"error": "group not found"}, status=404)
    group.delete()
    return JsonResponse({"deleted": True, "group_id": group_id})
