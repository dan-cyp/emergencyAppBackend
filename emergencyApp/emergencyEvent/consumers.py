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
        # text_data_json = json.loads(text_data)
        # lat = text_data_json["lat"]
        # lng = text_data_json["lat"]

        # event = {
        #     "type": "send_message",
        #     "lat": lat,
        #     "lng": lng
        # }

        # await self.channel_layer.group_send(self.group_name, event)

    
    async def send_message(self, event):
        await self.send(text_data=json.dumps(event))
        # lat = event['lat']
        # lng = event['lng']

        # await self.send(text_data=json.dumps(
        #     {
        #         "id": 1,
        #         "citizen": {
        #             "id": 1,
        #             "firstName": "joe mama",
        #             "lastName": "last",
        #             "phoneNumber": "123456789"
        #         },
        #         "latitude": lat, 
        #         "longitude": lng,
        #         "createdDateTime": "2023-03-09T08:06:07.612Z",
        #         "checked": False
        # }))

         