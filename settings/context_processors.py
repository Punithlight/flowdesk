from .models import UserSettings


def global_appearance(request):
    appearance = {
        "theme": "light",
        "font_size": 16,
        "high_contrast": False,
    }

    if request.user.is_authenticated:
        user_settings, created = UserSettings.objects.get_or_create(
            user=request.user
        )

        appearance = {
            "theme": user_settings.theme,
            "font_size": user_settings.font_size,
            "high_contrast": user_settings.high_contrast,
        }

    return {
        "global_appearance": appearance,
    }