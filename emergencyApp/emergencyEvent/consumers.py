import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EmergencyEventConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = 'emergencyEvents'

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
    
    async def disconnect(self, close_code):
        # leave group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from websocket
    async def receive(self, text_data):
        pass
    
    async def send_message(self, event):
        await self.send(text_data=json.dumps(event))

         