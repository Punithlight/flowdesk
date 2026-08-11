"""
URL configuration for flowkdesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path("admin/", admin.site.urls),
    path("employee/", include("employees.urls")),
    path("", include("accounts.urls")),

    path("dashboard/", include("dashboard.urls")),
    path('projects/',include('projects.urls')),
    path(
        'tasks/',
        include('tasks.urls')
    ),
    
    path(
        "reports/",
        include("reports.urls")
    ),
    path(
    "notifications/",
    include(("notifications.urls", "notifications"), namespace="notifications")
),
    path("assets/", include("assets.urls")),
    path("timesheets/", include("timesheets.urls")),
    path("helpdesk/", include("helpdesk.urls")),
     path(
        "leave/",
        include("leave_management.urls")
    ),
    path("leave/", include("leave_management.urls")),
    path("Calendar/", include("Calendar_app.urls")),
    path("settings/", include("settings.urls")),
    path("attendance/", include("attendance.urls")),
    path("manager/", include("manager_profile.urls")),
    path("teamchat/", include("teamchat.urls")),
     path("schedules/", include("schedules.urls")),
<<<<<<< HEAD
    path("teamlprofile/", include("teamlprofile.urls")),
=======
     

>>>>>>> c016af2abdd1292ae45c65dd9accffb82378e167
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    