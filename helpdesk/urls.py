from django.urls import path
from . import views

urlpatterns = [
    path("", views.helpdesk, name="helpdesk"),
]