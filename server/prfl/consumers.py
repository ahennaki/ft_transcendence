import json
from channels.generic.websocket         import AsyncWebsocketConsumer
from channels.layers                    import get_channel_layer
from .utils.connections_manager         import connected_clients, clients_lock
from authentication.utils               import print_red, print_green

class FriendshipRequestConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope["user"]
        if self.user:
            await self.close()
        await self.accept()
        print_green('Notification websocket .... connections accpted')
        async with clients_lock:
            connected_clients[self.user.username] = self.channel_name

    async def disconnect(self, close_code):
        async with clients_lock:
            if self.user.username in connected_clients:
                del connected_clients[self.user.username]
        print_red('Notification websocket ... connection closed')

    async def receive(self, text_data):
        pass

    async def send_friendship_request(self, event):
        await self.send(text_data=json.dumps({
            "type": "friendship_request",
            "from": event["from"]
        }))

    async def handle_friendship_request(self, event):
        await self.send(text_data=json.dumps({
            "type": "handle_friendship_request",
            "from": event["from"],
            "status": event["status"]
        }))
