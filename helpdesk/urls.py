from django.urls import path
from . import views

app_name = "helpdesk"

urlpatterns = [
    path(
        "",
        views.helpdesk,
        name="helpdesk"
    ),

    path(
        "technical-support/",
        views.TechnicalSupport,
        name="technical_support"
    ),
]