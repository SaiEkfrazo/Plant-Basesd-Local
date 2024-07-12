# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = 'notifications'

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         print('connected')
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         pass

#     async def send_notification(self, event):
#         notification = event['notification']

#         await self.send(text_data=json.dumps({
#             'notification': notification
#         }))


import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get plant_id from query parameters
        self.plant_id = self.scope['url_route']['kwargs']['plant_id']
        self.room_group_name = f'notifications_{self.plant_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        notification = event['notification']

        await self.send(text_data=json.dumps({
            'notification': notification
        }))
