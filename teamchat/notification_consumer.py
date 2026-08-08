import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{self.scope['user'].id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        print(
            "NOTIFICATION CONNECTED:",
            self.scope["user"].username
        )


    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )


    async def notify_call(self, event):

        print("CALL NOTIFICATION SENT:", event)

        await self.send(
            text_data=json.dumps(
                {
                    "type": "incoming_call",
                    "caller_id": event["caller_id"],
                    "caller_name": event["caller_name"],
                    "room_name": event["room_name"],
                    "call_type": event["call_type"],
                }
            )
        )