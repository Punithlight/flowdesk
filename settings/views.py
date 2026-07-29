import json

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import ActiveSession, LoginHistory, UserSettings


@login_required
def settings_page(request):
    settings_obj, created = UserSettings.objects.get_or_create(
        user=request.user
    )

    history = LoginHistory.objects.filter(
        user=request.user
    ).order_by("-login_time")

    sessions = ActiveSession.objects.filter(
        user=request.user
    ).order_by("-login_time")

    settings_data = {
        "two_fa_enabled": settings_obj.two_fa_enabled,
        "two_fa_method": settings_obj.two_fa_method,
        "biometric_enabled": settings_obj.biometric_enabled,
        "biometric_type": settings_obj.biometric_type,
        "recovery_email": settings_obj.recovery_email,
        "recovery_phone": settings_obj.recovery_phone,
        "security_question": settings_obj.security_question,
        "theme": settings_obj.theme,
        "font_size": settings_obj.font_size,
        "high_contrast": settings_obj.high_contrast,
        "notify_email": settings_obj.notify_email,
        "notify_push": settings_obj.notify_push,
        "notify_attendance": settings_obj.notify_attendance,
        "notify_announcements": settings_obj.notify_announcements,
        "language": settings_obj.language,
        "date_format": settings_obj.date_format,
        "time_format": settings_obj.time_format,
        "timezone": settings_obj.timezone,
        "dashboard_layout": settings_obj.dashboard_layout,
        "dashboard_widgets": settings_obj.dashboard_widgets,
    }

    history_data = []

    for row in history:
        history_data.append({
            "datetime": timezone.localtime(
                row.login_time
            ).strftime("%d-%m-%Y %I:%M %p"),
            "device": row.device,
            "location": row.location,
            "ip": row.ip_address,
        })

    sessions_data = []

    for session in sessions:
        sessions_data.append({
            "device": session.device,
            "location": session.location,
            "ip": session.ip_address,
            "time": timezone.localtime(
                session.login_time
            ).strftime("%d-%m-%Y %I:%M %p"),
            "current": session.is_current,
        })

    context = {
        "settings_data": settings_data,
        "history_data": history_data,
        "sessions_data": sessions_data,
    }

    return render(
        request,
        "settings/settings.html",
        context,
    )


@login_required
@require_POST
def settings_save(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid settings data.",
        }, status=400)

    settings_obj, created = UserSettings.objects.get_or_create(
        user=request.user
    )

    allowed_fields = [
        "two_fa_enabled",
        "two_fa_method",
        "biometric_enabled",
        "biometric_type",
        "recovery_email",
        "recovery_phone",
        "security_question",
        "theme",
        "font_size",
        "high_contrast",
        "notify_email",
        "notify_push",
        "notify_attendance",
        "notify_announcements",
        "language",
        "date_format",
        "time_format",
        "timezone",
        "dashboard_layout",
        "dashboard_widgets",
    ]

    for field in allowed_fields:
        if field in data:
            setattr(settings_obj, field, data[field])

    settings_obj.save()

    return JsonResponse({
        "success": True,
        "message": "Settings saved successfully.",
    })


@login_required
@require_POST
def settings_change_password(request):
    current_password = request.POST.get("current_password")
    new_password = request.POST.get("new_password")
    confirm_password = request.POST.get("confirm_password")

    if not current_password or not new_password or not confirm_password:
        return JsonResponse({
            "success": False,
            "error": "Please fill in all password fields.",
        }, status=400)

    if not request.user.check_password(current_password):
        return JsonResponse({
            "success": False,
            "error": "Current password is incorrect.",
        }, status=400)

    if new_password != confirm_password:
        return JsonResponse({
            "success": False,
            "error": "Passwords do not match.",
        }, status=400)

    if len(new_password) < 8:
        return JsonResponse({
            "success": False,
            "error": "Password must contain at least 8 characters.",
        }, status=400)

    request.user.set_password(new_password)
    request.user.save()

    update_session_auth_hash(request, request.user)

    return JsonResponse({
        "success": True,
        "message": "Password changed successfully.",
    })


@login_required
@require_POST
def logout_all_devices(request):
    ActiveSession.objects.filter(
        user=request.user
    ).exclude(
        is_current=True
    ).delete()

    return JsonResponse({
        "success": True,
        "message": "Logged out from all other devices.",
    })