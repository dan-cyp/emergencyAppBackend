import time
import json
from channels.generic.websocket import WebsocketConsumer

class EmergencyEventConsumer(WebsocketConsumer):
    # def sendRandomData(self):
    #     self.send(text_data=json.dumps({
            
    # })) 

    def connect(self):
        self.accept()

        print("New connection established")

        self.send(text_data=json.dumps({
            'type':'connection_established',
            'message':'You are now connected!'
        }))
        while True:
            self.sendMessage({'message':'123'})
            time.sleep(1)
    
    def sendMessage(self, message):
        self.send(text_data=json.dumps(message))

         