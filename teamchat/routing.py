from django.urls import path

from .consumers import CallConsumer
from .notification_consumer import NotificationConsumer

websocket_urlpatterns = [

    path(
        "ws/call/<str:room_name>/",
        CallConsumer.as_asgi(),
    ),

    path(
        "ws/notify/",
        NotificationConsumer.as_asgi(),
    ),

]