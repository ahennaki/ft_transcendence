from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db                import database_sync_to_async
from .models                    import PlayerQueue, Match
from prfl.models                import Profile
from prfl.serializers           import ProfileSerializer
from authentication.utils       import print_red, print_green, print_yellow
from .game_loop                 import game_loop
from .paddle                    import update_paddle, move_paddle
from .helpers                   import initialize_data, score_update
from .game_end                  import end_game
from .matchmaking               import matchmaking
import json
import time
import asyncio

active_connections = {}
# invite_players = {}

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        profile_exists = await self.check_user_profile()
        print_green(f'{self.user.username} is connected')
        self.isGaming = False
        if not self.user.is_authenticated or not profile_exists:
            await self.close()
            return
        if self.user.id not in active_connections:
            active_connections[self.user.id] = 0
        active_connections[self.user.id] += 1

        await self.accept()

        if active_connections[self.user.id] > 1:
            data = {'type': 'already_connected', 'message': 'User already connected from another tab'}
            await self.send(text_data=json.dumps({'type': 'already_connected', 'data': data}))
            await self.close()
            return

        self.group_name = f"user_{self.user.username}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await initialize_data(self)

    async def disconnect(self, close_code):
        print_red(f'{self.user.username} is disconected!')
        if self.user.id in active_connections:
            active_connections[self.user.id] -= 1
            if active_connections[self.user.id] == 0:
                del active_connections[self.user.id]
        if hasattr(self, 'group_name'):
            if self.isGaming:
                await end_game(self, True)
            self.isGaming = False
            await self.remove_player_from_queue()
            await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'join_queue':
            await self.add_player_to_queue()
            await matchmaking(self)
        # elif action == 'invitation':
            # if self.user.id not in invite_players:
            #     invite_players[self.user.id] = 0
            # await invited_player(self, data)
        elif action == 'disconnect':
            self.isGaming = False
            await self.close()
        elif action == 'start_game':
            await self.start_game(data)
        elif action == 'move_paddle':
            await move_paddle(self, data)
        elif action == 'update_paddle':
            await update_paddle(self, data)
        elif action == 'score_update':
            await score_update(self, data)
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Unknown action'}))

    async def start_game(self, data):
        print_green(f'{self.user.username} start the game!')
        self.start_time = time.time()
        self.isGaming = True
        self.match_id = data['match_id']
        self.match, self.player1_username, self.player2_username = await self.get_player_usernames(self.match_id)
        if self.user.username == self.player1_username:
            asyncio.create_task(game_loop(self))

    async def send_match_info(self, event):
        self.player_number = event['player_number']
        await self.send(text_data=json.dumps({
            'player': event['player'], 'match_id': event['match_id'],
            'type': 'match_found', 'player_number': self.player_number}))

    async def waiting(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    async def no_match_found(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    async def game_update(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    async def paddle_update(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    async def score_update(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    async def end_game(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def get_player_usernames(self, match_id):
        try:
            match = Match.objects.get(id=match_id)
            return match, match.player1.user.username, match.player2.user.username
        except Match.DoesNotExist:
            return None, None, None

    @database_sync_to_async
    def get_match_status(self, match_id):
        try:
            match = Match.objects.get(id=match_id)
            return match.status
        except Match.DoesNotExist:
            return None

    @database_sync_to_async
    def check_user_profile(self):
        try:
            return self.user.profile is not None
        except Profile.DoesNotExist:
            return False

    @database_sync_to_async
    def add_player_to_queue(self):
        profile = self.user.profile
        PlayerQueue.objects.get_or_create(player=profile)

    @database_sync_to_async
    def remove_player_from_queue(self):
        profile = self.user.profile
        PlayerQueue.objects.filter(player=profile).delete()
