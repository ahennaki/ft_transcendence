import json

from asgiref.sync               import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers            import get_channel_layer
from chat.models                import Chat, Message
from prfl.models                import Profile
from django.core.exceptions     import ObjectDoesNotExist
from django.contrib.auth.models import User
from authentication.utils       import print_red, print_green, print_yellow
from asyncio                    import Lock

user_connections = {}
connections_lock = Lock()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print_red(f'USER ... websocket: {self.user.username}')
        if not self.user:
            await self.close()
        
        await self.accept()
        print_green('websocket .... connections accpted')
        async with connections_lock:
            user_connections[self.user.username] = self.channel_name
        profile = await sync_to_async(self.get_profile)(self.user)
        profile.is_online = True
        await sync_to_async(profile.save)()

    async def disconnect(self, code):
        async with connections_lock:
            if self.user.username in user_connections:
                del user_connections[self.user.username]
        print_red('websocket ... connection closed')
        profile = await sync_to_async(self.get_profile)(self.user)
        profile.is_online = False
        await sync_to_async(profile.save)()

    async def receive(self, text_data):
        print_green('websocket ... receiving')
        data_json = json.loads(text_data)
        if not data_json:
            pass
        target_username = data_json['username']
        message_content = data_json['message']
        print_yellow(target_username)
        username = await sync_to_async(self.get_username)()
        profile = await sync_to_async(self.get_profile)(self.user)
        room_name = username + '-' + target_username
        try:
            user = await sync_to_async(Profile.objects.get)(username=target_username)
        except ObjectDoesNotExist:
            pass
        try:
            chat = await sync_to_async(Chat.objects.get)(name=room_name)
        except ObjectDoesNotExist:
            chat = await sync_to_async(Chat.objects.create)(
                user1=profile,
                user2=user,
                name=room_name
            )
        print_yellow(message_content)
        message = await sync_to_async(Message.objects.create)(
            chat=chat,
            sender=profile,
            receiver=user,
            content=message_content
        )
        created_at =  await sync_to_async(self.get_time)(message)
        message_data = {
                'type': 'chat_message',
                'from': username,
                'message': message_content,
                'created_at':created_at,
        }
        async with connections_lock:
            target_channel = user_connections[target_username]
        if target_channel:
            print_red("exist")
            await self.channel_layer.send(
                target_channel,
                message_data
            )

    async def chat_message(self, event):
        print_green('websocket ... send message to websocket')
        print(event)
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'from': event['from'],
            'message': event['message'],
            'created_at': event['created_at']
        }))
    # async def load_history(self, room_name, offset):
    #     print_green('websocket ... load messages')
    #     chat = await sync_to_async(Chat.objects.get)(name=room_name)
    #     messages = await sync_to_async(list)(
    #         Message.objects.filter(chat=chat).order_by('-created_at')[offset:offset+20]
    #     )

    #     await self.send(text_data=json.dumps({
    #         'type': 'load_messages',
    #         'messages': [{
    #             'id': message.id,
    #             'sender_id': message.sender_id,
    #             'receiver_id': message.receive_id,
    #             'content': message.content,
    #             'created_at': message.created_at.isoformat(),
    #             'is_read': message.is_read
    #         } for message in messages]
    #     }))

    # async def set_read(message_id):
    #     message = await sync_to_async(Message.objects.get)(id=message_id)
    #     message.is_read = True
    #     await sync_to_async(message.save)()

        
    def get_profile(self, user):
        return user.profile
    def get_username(self):
        return self.user.username
    def get_time(self, message):
        return message.created_at.isoformat()