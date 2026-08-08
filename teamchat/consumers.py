print("CONSUMER IMPORTED")

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CallConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("========== CONNECT CALLED ==========")

        print("PATH:", self.scope["path"])
        print("USER:", self.scope["user"])

        try:
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        except Exception as e:
            print("ROOM NAME ERROR:", e)
            await self.close()
            return

        self.room_group_name = f"call_{self.room_name}"

        print("ROOM:", self.room_name)
        print("GROUP:", self.room_group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print("========== WEBSOCKET ACCEPTED ==========")


    async def disconnect(self, close_code):

        print("========== DISCONNECTED ==========")
        print("CODE:", close_code)

        if hasattr(self, "room_group_name"):

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )


    async def receive(self, text_data):

        print("========== MESSAGE RECEIVED ==========")
        print(text_data)

        try:
            data = json.loads(text_data)

        except Exception as e:
            print("JSON ERROR:", e)
            return


        print("SIGNAL DATA:", data)


        await self.channel_layer.group_send(

            self.room_group_name,

            {
                "type": "signal_message",
                "message": data,
                "sender_channel": self.channel_name,
            }

        )


    async def signal_message(self, event):

        print("========== SIGNAL FORWARD ==========")

        if event["sender_channel"] == self.channel_name:
            print("Same sender, skipping")
            return


        print("Sending to client:", event["message"])


        await self.send(

            text_data=json.dumps(
                event["message"]
            )

        )