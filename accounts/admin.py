from django.contrib import admin

from .models import UserProfile
from .models import LoginHistory

admin.site.register(UserProfile)
admin.site.register(LoginHistory)